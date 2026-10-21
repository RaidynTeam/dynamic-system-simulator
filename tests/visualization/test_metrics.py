"""Error metrics must match an independently hand-computed expectation."""

from math import sqrt

import numpy as np
import pytest

from dss.analytical import solve_analytical
from dss.contracts import ErrorMetrics, ModelParams, Response, SimulationConfig
from dss.numerical import make_time_grid, solve_euler, solve_rk4
from dss.visualization import compute_error, error_signal


def response(method, y, t=None, v=None):
    y = np.asarray(y, dtype=np.float64)
    t = np.arange(y.size, dtype=np.float64) if t is None else np.asarray(t, dtype=np.float64)
    v = np.zeros_like(y) if v is None else np.asarray(v, dtype=np.float64)
    return Response(t=t, y=y, v=v, method=method)


def real_pair(a1=1.0, dt=0.2, t_end=6.0, solver=solve_euler):
    model = ModelParams(a1=a1, a0=1.0, b0=1.0)
    t = make_time_grid(SimulationConfig(t0=0.0, t_end=t_end, dt=dt))
    return solve_analytical(model, t), solver(model, t)


# --- the worked example from the task guide ----------------------------------


def test_the_hand_computed_example_from_the_guide():
    # reference.y = [0, 1, 2] against candidate.y = [0, 2, 0]
    # absolute difference [0, 1, 2] -> max 2, RMSE sqrt((0 + 1 + 4) / 3)
    reference = response("analytical", [0.0, 1.0, 2.0])
    candidate = response("euler", [0.0, 2.0, 0.0])

    assert np.array_equal(error_signal(reference, candidate), [0.0, 1.0, 2.0])
    metrics = compute_error(reference, candidate)
    assert metrics.max_abs == 2.0
    assert metrics.rmse == pytest.approx(sqrt(5.0 / 3.0), rel=1e-15)


def test_the_result_is_a_shared_error_metrics_object():
    metrics = compute_error(*real_pair())
    assert isinstance(metrics, ErrorMetrics)
    assert metrics.max_abs >= 0 and metrics.rmse >= 0
    assert np.isfinite([metrics.max_abs, metrics.rmse]).all()


def test_an_identical_signal_has_exactly_zero_error():
    reference = response("analytical", [0.0, 0.5, 1.0])
    same = response("rk4", [0.0, 0.5, 1.0])
    metrics = compute_error(reference, same)
    assert metrics.max_abs == 0.0
    assert metrics.rmse == 0.0


def test_a_response_compared_with_itself_is_zero():
    reference, _ = real_pair()
    metrics = compute_error(reference, reference)
    assert metrics.max_abs == 0.0 and metrics.rmse == 0.0


def test_rmse_never_exceeds_the_maximum_absolute_error():
    # A root mean square of values bounded by max cannot exceed max.
    for a1 in (1.0, 2.0, 3.0):
        for solver in (solve_euler, solve_rk4):
            metrics = compute_error(*real_pair(a1=a1, solver=solver))
            assert metrics.rmse <= metrics.max_abs + 1e-15


def test_a_constant_offset_makes_both_metrics_that_offset():
    reference = response("analytical", [0.0, 1.0, 2.0, 3.0])
    shifted = response("euler", [0.5, 1.5, 2.5, 3.5])
    metrics = compute_error(reference, shifted)
    assert metrics.max_abs == pytest.approx(0.5)
    assert metrics.rmse == pytest.approx(0.5)


# --- what the metric deliberately ignores ------------------------------------


def test_only_y_is_measured_and_velocity_is_ignored():
    t = np.array([0.0, 1.0, 2.0], dtype=np.float64)
    y = np.array([0.0, 1.0, 2.0], dtype=np.float64)
    quiet = Response(t=t, y=y, v=np.zeros(3), method="analytical")
    loud = Response(t=t, y=y, v=np.array([0.0, 900.0, -900.0]), method="euler")
    metrics = compute_error(quiet, loud)
    assert metrics.max_abs == 0.0 and metrics.rmse == 0.0


def test_the_metric_is_symmetric_because_it_uses_absolute_differences():
    reference, candidate = real_pair()
    forward = compute_error(reference, candidate)
    backward = compute_error(candidate, reference)
    assert forward.max_abs == backward.max_abs
    assert forward.rmse == backward.rmse


# --- rejected input ----------------------------------------------------------


def test_different_time_grids_are_rejected_instead_of_interpolated():
    coarse = response("analytical", [0.0, 1.0, 2.0], t=[0.0, 1.0, 2.0])
    fine = response("euler", [0.0, 1.0, 2.0], t=[0.0, 0.5, 1.0])
    with pytest.raises(ValueError, match="time grid"):
        compute_error(coarse, fine)
    with pytest.raises(ValueError, match="time grid"):
        error_signal(coarse, fine)


def test_a_longer_grid_is_rejected_rather_than_truncated():
    short = response("analytical", [0.0, 1.0, 2.0])
    long = response("euler", [0.0, 1.0, 2.0, 3.0])
    with pytest.raises(ValueError, match="time grid"):
        compute_error(short, long)


@pytest.mark.parametrize("bad", [None, "euler", 3, [1.0, 2.0], np.zeros(3)])
def test_anything_that_is_not_a_response_is_rejected(bad):
    reference, candidate = real_pair()
    with pytest.raises(ValueError):
        compute_error(bad, candidate)
    with pytest.raises(ValueError):
        compute_error(reference, bad)


def test_a_corrupted_response_is_caught_by_the_shared_validator():
    reference, candidate = real_pair()
    object.__setattr__(candidate, "y", np.full(candidate.y.size, np.nan))
    with pytest.raises(ValueError):
        compute_error(reference, candidate)


def test_the_call_does_not_modify_the_supplied_arrays():
    reference, candidate = real_pair()
    before = [(r.t.copy(), r.y.copy(), r.v.copy()) for r in (reference, candidate)]
    compute_error(reference, candidate)
    for result, (t, y, v) in zip((reference, candidate), before):
        assert np.array_equal(result.t, t)
        assert np.array_equal(result.y, y)
        assert np.array_equal(result.v, v)


# --- numerical range ---------------------------------------------------------


def test_rmse_survives_values_where_the_naive_formula_overflows():
    reference = response("analytical", [0.0, 0.0, 0.0])
    huge = response("euler", [0.0, 1e200, 2e200])

    difference = huge.y - reference.y
    with np.errstate(over="ignore"):
        naive = np.mean(difference * difference)
    assert not np.isfinite(naive)  # the contract's literal formula overflows

    metrics = compute_error(reference, huge)
    assert metrics.max_abs == 2e200
    assert metrics.rmse == pytest.approx(2e200 * sqrt(5.0 / 3.0) / 2.0, rel=1e-12)
    assert np.isfinite(metrics.rmse)


# --- against the real solvers ------------------------------------------------


@pytest.mark.parametrize("a1", [1.0, 2.0, 3.0])
def test_rk4_beats_euler_on_the_same_grid(a1):
    reference, euler = real_pair(a1=a1, solver=solve_euler)
    _, rk4 = real_pair(a1=a1, solver=solve_rk4)
    assert compute_error(reference, rk4).max_abs < compute_error(reference, euler).max_abs


@pytest.mark.parametrize("solver", [solve_euler, solve_rk4])
def test_halving_the_step_reduces_the_error(solver):
    coarse = compute_error(*real_pair(dt=0.4, solver=solver)).max_abs
    fine = compute_error(*real_pair(dt=0.2, solver=solver)).max_abs
    finer = compute_error(*real_pair(dt=0.1, solver=solver)).max_abs
    assert finer < fine < coarse


def test_a_real_comparison_reports_a_nonzero_error():
    # Guards against a metric that silently returns zero for everything.
    metrics = compute_error(*real_pair(dt=0.4))
    assert metrics.max_abs > 0 and metrics.rmse > 0
