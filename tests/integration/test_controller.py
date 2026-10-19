"""Real owner APIs through the M4A controller; no plots or sample outputs."""

from itertools import permutations
from math import pi
from pathlib import Path
import subprocess
import sys
import textwrap

import numpy as np
import pytest

from dss import analytical, numerical
from dss.contracts import ModelParams, Response, SimulationConfig
from dss.ui.controller import run_simulation


METHODS = ("analytical", "euler", "rk4")
SELECTIONS = [selection for count in (1, 2, 3) for selection in permutations(METHODS, count)]


@pytest.mark.parametrize("a1", [1.0, 2.0, 3.0])
@pytest.mark.parametrize("methods", SELECTIONS)
def test_real_cases_method_selections_and_order(a1, methods):
    model = ModelParams(a1, 1.0, 1.0)
    config = SimulationConfig(0, 2.03, 0.04)
    outputs = run_simulation(model, config, methods)
    expected_t = numerical.make_time_grid(config)
    assert [response.method for response in outputs] == list(methods)
    for response in outputs:
        assert isinstance(response, Response)
        assert np.array_equal(response.t, expected_t)
        assert np.isfinite(response.y).all() and np.isfinite(response.v).all()
        assert response.y[0] == response.v[0] == 0
        assert response.t[0] == 0 and response.t[-1] == config.t_end
        assert response.y[-1] > 0


def test_one_grid_object_only_selected_solvers_and_preserved_parameters(monkeypatch):
    original_grid = numerical.make_time_grid
    original_rk4 = numerical.solve_rk4
    original_exact = analytical.solve_analytical
    model = ModelParams(3, 2, 2.5)
    config = SimulationConfig(0, 1.03, 0.1)
    grids = []
    calls = []

    def grid_spy(received_config):
        assert received_config is config
        grid = original_grid(received_config)
        grids.append(grid)
        return grid

    def record(method, solver):
        def wrapper(received_model, grid):
            assert received_model is model
            calls.append((method, grid))
            return solver(received_model, grid)
        return wrapper

    def unselected(*args):
        pytest.fail("Euler was not selected.")

    monkeypatch.setattr(numerical, "make_time_grid", grid_spy)
    monkeypatch.setattr(numerical, "solve_rk4", record("rk4", original_rk4))
    monkeypatch.setattr(analytical, "solve_analytical", record("analytical", original_exact))
    monkeypatch.setattr(numerical, "solve_euler", unselected)
    outputs = run_simulation(model, config, ("rk4", "analytical"))
    assert len(grids) == 1
    assert [method for method, grid in calls] == ["rk4", "analytical"]
    assert all(grid is grids[0] for method, grid in calls)
    assert np.array_equal(grids[0], original_grid(config))
    assert all(not np.shares_memory(response.t, grids[0]) for response in outputs)


@pytest.mark.parametrize("a1", [1.0, 2.0, 3.0])
def test_real_gain_scaling_and_parameter_changes(a1):
    config = SimulationConfig(0, 3, 0.05)
    baseline = run_simulation(ModelParams(a1, 1, 1), config, METHODS)
    scaled = run_simulation(ModelParams(a1, 1, 2.5), config, METHODS)
    changed = run_simulation(ModelParams(a1 + 0.5, 2, 1), config, METHODS)
    for original, amplified, different in zip(baseline, scaled, changed):
        assert np.array_equal(original.t, amplified.t)
        np.testing.assert_allclose(amplified.y, 2.5 * original.y, rtol=1e-12, atol=1e-14)
        np.testing.assert_allclose(amplified.v, 2.5 * original.v, rtol=1e-12, atol=1e-14)
        assert not np.allclose(original.y, different.y)


@pytest.mark.parametrize("a1", [1.0, 2.0, 3.0])
def test_reduced_dt_is_forwarded_and_reduces_real_numerical_error(a1):
    model = ModelParams(a1, 1, 1)
    initial_dt = 0.1 * 2 * pi
    errors = []
    for divisor in (1, 2, 4):
        config = SimulationConfig(0, 10, initial_dt / divisor)
        exact, euler, rk4 = run_simulation(model, config, METHODS)
        assert np.array_equal(exact.t, numerical.make_time_grid(config))
        assert np.array_equal(exact.t, euler.t) and np.array_equal(exact.t, rk4.t)
        errors.append([np.max(np.abs(candidate.y - exact.y)) for candidate in (euler, rk4)])
    assert np.all(np.array(errors[2]) < np.array(errors[1]))
    assert np.all(np.array(errors[1]) < np.array(errors[0]))


@pytest.mark.parametrize("methods", [(), ("euler", "euler"), ("Euler",), ("unknown",), ([],), (None,), None, "rk4"])
def test_invalid_methods_rejected_before_grid_generation(monkeypatch, methods):
    def forbidden(*args):
        pytest.fail("Invalid selection must not generate a grid.")
    monkeypatch.setattr(numerical, "make_time_grid", forbidden)
    with pytest.raises(ValueError):
        run_simulation(ModelParams(1, 1, 1), SimulationConfig(0, 1, 0.1), methods)


@pytest.mark.parametrize("target,field,value,match", [
    ("model", "a1", 0, "a1"), ("model", "b0", float("inf"), "b0"),
    ("config", "t0", 1, "t0"), ("config", "t_end", -1, "t_end"),
    ("config", "dt", 0, "dt"), ("config", "dt", float("nan"), "dt"),
])
def test_controller_revalidates_shared_objects(monkeypatch, target, field, value, match):
    model = ModelParams(1, 1, 1)
    config = SimulationConfig(0, 1, 0.1)
    # Simulate a corrupted external object to test controller-side validation,
    # bypassing the shared frozen constructor only inside this test.
    object.__setattr__(model if target == "model" else config, field, value)
    def forbidden(*args):
        pytest.fail("Invalid inputs must not generate a grid.")
    monkeypatch.setattr(numerical, "make_time_grid", forbidden)
    with pytest.raises(ValueError, match=match):
        run_simulation(model, config, METHODS)


def test_sample_limit_error_propagates():
    with pytest.raises(ValueError, match="1,000,000 samples"):
        run_simulation(ModelParams(1, 1, 1), SimulationConfig(0, 1, 1e-9), ("analytical",))


@pytest.mark.parametrize("method,model,message", [
    ("analytical", ModelParams(1, 1, 1e308), "float64 calculation range"),
    ("euler", ModelParams(1e308, 1, 1), "Euler calculation overflowed"),
    ("rk4", ModelParams(1e308, 1, 1), "RK4 calculation overflowed"),
])
def test_real_numerical_failures_propagate(method, model, message):
    with pytest.raises(FloatingPointError, match=message):
        run_simulation(model, SimulationConfig(0, 10, 1), (method,))


def test_error_identity_and_no_partial_success_or_later_solver(monkeypatch):
    failure = FloatingPointError("Owner's original numerical failure")
    def fail(*args):
        raise failure
    def forbidden(*args):
        pytest.fail("Do not continue after a failed selected solver.")
    monkeypatch.setattr(numerical, "solve_euler", fail)
    monkeypatch.setattr(numerical, "solve_rk4", forbidden)
    with pytest.raises(FloatingPointError) as raised:
        run_simulation(ModelParams(1, 1, 1), SimulationConfig(0, 1, 0.1), METHODS)
    assert raised.value is failure


def test_compatible_list_selection_preserves_order():
    outputs = run_simulation(ModelParams(1, 1, 1), SimulationConfig(0, 1, 0.1), ["rk4", "analytical"])
    assert [response.method for response in outputs] == ["rk4", "analytical"]


@pytest.mark.parametrize("methods", [METHODS, ("rk4",)])
def test_real_controller_runs_without_qt_or_visualization_imports(methods):
    script = textwrap.dedent(f'''
        import importlib.abc
        import sys
        class BlockPresentation(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if fullname.split(".")[0] in ("PySide6", "matplotlib") or fullname.startswith("dss.visualization"):
                    raise AssertionError("Controller imported presentation code: " + fullname)
                return None
        sys.meta_path.insert(0, BlockPresentation())
        from dss.contracts import ModelParams, SimulationConfig
        from dss.ui.controller import run_simulation
        methods = {methods!r}
        result = run_simulation(ModelParams(1, 1, 1), SimulationConfig(0, 1, 0.1), methods)
        assert tuple(response.method for response in result) == methods
        if "analytical" not in methods:
            assert "dss.analytical" not in sys.modules
    ''')
    result = subprocess.run(
        [sys.executable, "-c", script], cwd=Path(__file__).resolve().parents[2],
        text=True, capture_output=True, timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
