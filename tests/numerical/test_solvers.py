"""Independent checks against the Word formulae and hand calculations."""

import numpy as np
import pytest

from dss.contracts import ModelParams, SimulationConfig
from dss.numerical import make_time_grid, solve_euler, solve_rk4


def test_euler_uses_old_y_and_v_for_both_updates():
    result = solve_euler(ModelParams(2., 1., 1.), np.array([0., .1, .2]))
    np.testing.assert_allclose(result.y, [0., 0., .01])
    np.testing.assert_allclose(result.v, [0., .1, .18])


def test_euler_uses_actual_short_final_step():
    t = make_time_grid(SimulationConfig(0., .15, .1))
    result = solve_euler(ModelParams(2., 1., 1.), t)
    np.testing.assert_allclose(result.y, [0., 0., .005])
    np.testing.assert_allclose(result.v, [0., .1, .14])


def test_rk4_first_step_matches_hand_calculation():
    # h=.1: k1=(0,1), k2=(.05,.9), k3=(.045,.9075), k4=(.09075,.814).
    result = solve_rk4(ModelParams(2., 1., 1.), np.array([0., .1]))
    assert result.y[1] == pytest.approx(1123 / 240000, rel=1e-14)
    assert result.v[1] == pytest.approx(5429 / 60000, rel=1e-14)


def exact_response(model, t):
    """Direct Word (8)-(10) and their derivatives, only for well-scaled tests."""
    sigma = model.a1 / 2
    gain = model.b0 / model.a0
    d = sigma**2 - model.a0
    if d < 0:
        omega = np.sqrt(-d)
        decay = np.exp(-sigma * t)
        y = gain * (1 - decay * (np.cos(omega*t) + sigma/omega*np.sin(omega*t)))
        v = model.b0 / omega * decay * np.sin(omega*t)
    elif d == 0:
        y = gain * (1 - (1 + sigma*t) * np.exp(-sigma*t))
        v = model.b0 * t * np.exp(-sigma*t)
    else:
        s1, s2 = -sigma + np.sqrt(d), -sigma - np.sqrt(d)
        y = gain * (1 + (s2*np.exp(s1*t) - s1*np.exp(s2*t)) / (s1-s2))
        v = model.b0 * (np.exp(s1*t) - np.exp(s2*t)) / (s1-s2)
    return y, v


@pytest.mark.parametrize("values", [
    (1., 1., 1.), (2., 1., 1.), (3., 1., 1.),
    (2., 4., 2.), (4., 4., 2.), (6., 4., 2.),
])
def test_all_three_cases_match_independent_word_formulae(values):
    model = ModelParams(*values)
    t = make_time_grid(SimulationConfig(0., 2., .005))
    expected_y, expected_v = exact_response(model, t)
    euler = solve_euler(model, t)
    rk4 = solve_rk4(model, t)
    for result, tolerance in [(euler, .02), (rk4, 1e-8)]:
        np.testing.assert_allclose(result.y, expected_y, rtol=0, atol=tolerance)
        np.testing.assert_allclose(result.v, expected_v, rtol=0, atol=tolerance)
    assert np.max(abs(rk4.y - expected_y)) < np.max(abs(euler.y - expected_y))


@pytest.mark.parametrize("solver", [solve_euler, solve_rk4])
def test_irregular_grid_initial_state_ownership_and_gain_scaling(solver):
    t = np.array([0., .001, .004, .005, .012, .02])
    original = t.copy()
    result = solver(ModelParams(2., 1., 1.), t)
    scaled = solver(ModelParams(2., 1., 3.), t)
    expected_y, expected_v = exact_response(ModelParams(2., 1., 1.), t)
    tolerance = 1e-4 if solver is solve_euler else 1e-11
    np.testing.assert_allclose(result.y, expected_y, rtol=0, atol=tolerance)
    np.testing.assert_allclose(result.v, expected_v, rtol=0, atol=2*tolerance)
    np.testing.assert_allclose(scaled.y, 3*result.y)
    np.testing.assert_allclose(scaled.v, 3*result.v)
    assert result.y[0] == result.v[0] == 0
    assert result.method == ("euler" if solver is solve_euler else "rk4")
    np.testing.assert_array_equal(t, original)
    np.testing.assert_array_equal(result.t, original)
    assert not np.shares_memory(result.t, t)
    assert not np.shares_memory(result.y, result.v)


@pytest.mark.parametrize("solver", [solve_euler, solve_rk4])
@pytest.mark.parametrize("t", [
    [0., 1.], np.array([0, 1]), np.array([0., 1.], dtype=np.float32),
    np.array([]), np.array([0.]), np.array([[0., 1.]]),
    np.array([1., 2.]), np.array([0., .1, .1]), np.array([0., .2, .1]),
    np.array([0., np.inf]), np.array([0., np.nan]),
])
def test_invalid_grid_is_rejected(solver, t):
    with pytest.raises(ValueError):
        solver(ModelParams(2., 1., 1.), t)


@pytest.mark.parametrize("solver", [solve_euler, solve_rk4])
def test_arithmetic_overflow_is_reported(solver):
    with pytest.raises(FloatingPointError):
        solver(ModelParams(1e308, 1., 1e308), np.array([0., 1., 2.]))


def test_euler_does_not_silently_fix_an_unstable_step():
    t = make_time_grid(SimulationConfig(0., 30., 3.))
    result = solve_euler(ModelParams(2., 1., 1.), t)
    np.testing.assert_array_equal(result.t, t)
    assert np.max(abs(result.y)) > 100  # The physical response tends to 1.


@pytest.mark.parametrize("solver,lower,upper", [
    (solve_euler, 1.8, 2.3), (solve_rk4, 14., 19.),
])
def test_endpoint_convergence_at_two_seconds(solver, lower, upper):
    model = ModelParams(2., 1., 1.)
    expected = 1 - 3*np.exp(-2.)
    errors = []
    for h in [.1, .05, .025]:
        t = make_time_grid(SimulationConfig(0., 2., h))
        errors.append(abs(solver(model, t).y[-1] - expected))
    ratios = np.array(errors[:-1]) / errors[1:]
    assert np.all((ratios > lower) & (ratios < upper))
