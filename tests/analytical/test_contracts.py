from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from dss.contracts import ErrorMetrics, ModelParams, Response, SimulationConfig


@pytest.mark.parametrize("field", ["a1", "a0", "b0"])
@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf"), -float("inf"), True, "1", None])
def test_model_rejects_invalid_coefficients(field, bad):
    values = dict(a1=1.0, a0=1.0, b0=1.0)
    values[field] = bad
    with pytest.raises(ValueError, match=field):
        ModelParams(**values)


def test_model_is_frozen_and_accepts_numpy_real_coefficients():
    model = ModelParams(a1=np.float64(1), a0=1, b0=2)
    with pytest.raises(FrozenInstanceError):
        model.a1 = 3


@pytest.mark.parametrize("values", [(1, 10, .1), (0, 0, .1), (0, -1, .1), (0, 10, 0), (0, 10, -1), (0, float("inf"), .1), (0, 10, float("nan"))])
def test_config_rejects_invalid_intervals(values):
    with pytest.raises(ValueError):
        SimulationConfig(*values)


def test_config_allows_shorter_interval_than_step():
    assert SimulationConfig(0, .01, .1).dt == .1


def samples():
    return dict(t=np.array([0., .1, .2]), y=np.zeros(3), v=np.zeros(3), method="analytical")


@pytest.mark.parametrize("field,bad", [
    ("t", np.array([0., .1, .1])),
    ("t", np.array([0., .2, .1])),
    ("t", np.array([1., 2., 3.])),
    ("y", np.zeros(2)),
    ("v", np.array([0., np.nan, 0.])),
    ("y", np.array([0., np.inf, 0.])),
    ("y", np.zeros((3, 1))),
    ("y", np.zeros(3, dtype=np.float32)),
    ("y", [0., 0., 0.]),
    ("t", np.array([0.])),
    ("method", "demo"),
])
def test_response_rejects_invalid_samples(field, bad):
    values = samples()
    values[field] = bad
    with pytest.raises(ValueError):
        Response(**values)


@pytest.mark.parametrize("method", ["analytical", "euler", "rk4"])
def test_response_owns_samples_without_changing_inputs(method):
    values = samples()
    values["method"] = method
    response = Response(**values)
    for field in ("t", "y", "v"):
        assert np.array_equal(getattr(response, field), values[field])
        assert not np.shares_memory(getattr(response, field), values[field])
    values["y"][1] = 5
    assert response.y[1] == 0


@pytest.mark.parametrize("field", ["max_abs", "rmse"])
@pytest.mark.parametrize("bad", [-1., float("nan"), float("inf")])
def test_metrics_reject_invalid_values(field, bad):
    values = dict(max_abs=0., rmse=0.)
    values[field] = bad
    with pytest.raises(ValueError, match=field):
        ErrorMetrics(**values)
