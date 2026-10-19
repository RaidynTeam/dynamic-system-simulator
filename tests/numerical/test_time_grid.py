import numpy as np
import pytest

from dss.contracts import SimulationConfig
from dss.numerical import make_time_grid
from dss.numerical.time_grid import MAX_SAMPLES


@pytest.mark.parametrize("end,dt,expected", [
    (1., .3, [0., .3, .6, .9, 1.]),
    (1., 2., [0., 1.]),
    (1., 1., [0., 1.]),
    (1., .25, [0., .25, .5, .75, 1.]),
    (.3, .1, [0., .1, .2, .3]),
    (.1 + .2, .1, [0., .1, .2, .1 + .2]),
    (1e-20, 1e-21, np.linspace(0., 1e-20, 11)),
    (1e-20, 1., [0., 1e-20]),
])
def test_grid_preserves_interval_and_step(end, dt, expected):
    t = make_time_grid(SimulationConfig(0., end, dt))
    assert t.dtype == np.float64
    np.testing.assert_allclose(t, expected, rtol=1e-14, atol=0)
    assert t[0] == 0 and t[-1] == end
    assert np.all(t[1:] > t[:-1])
    assert np.all(t <= end)


@pytest.mark.parametrize("end", [np.nextafter(1., 0.), np.nextafter(1., np.inf)])
def test_roundoff_does_not_create_an_extra_endpoint(end):
    t = make_time_grid(SimulationConfig(0., end, .1))
    assert len(t) == 11
    assert t[-1] == end
    assert np.all(np.diff(t) > 0)


def test_sample_limit_includes_both_endpoints():
    t = make_time_grid(SimulationConfig(0., MAX_SAMPLES - 1, 1.))
    assert len(t) == MAX_SAMPLES
    with pytest.raises(ValueError, match="1,000,000"):
        make_time_grid(SimulationConfig(0., MAX_SAMPLES - .5, 1.))
    with pytest.raises(ValueError, match="1,000,000"):
        make_time_grid(SimulationConfig(0., MAX_SAMPLES, 1.))


@pytest.mark.parametrize("end,dt", [(1., 1e-20), (1e308, 1e-308)])
def test_excessive_request_is_rejected_before_allocation(end, dt):
    with pytest.raises(ValueError, match="1,000,000"):
        make_time_grid(SimulationConfig(0., end, dt))


@pytest.mark.parametrize("values", [
    (1., 2., .1), (0., 0., .1), (0., -1., .1),
    (0., 1., 0.), (0., 1., -.1),
    (0., np.inf, .1), (0., 1., np.nan),
])
def test_invalid_configuration_is_rejected(values):
    with pytest.raises(ValueError):
        make_time_grid(SimulationConfig(*values))
