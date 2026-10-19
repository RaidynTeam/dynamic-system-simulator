from decimal import Decimal, localcontext

import numpy as np
import pytest

from dss.analytical import solve_analytical
from dss.contracts import ModelParams


def test_handout_case_two_matches_independent_decimal_values():
    t = np.array([0., .01, .5, 1., 2., 10.])
    with localcontext() as ctx:
        ctx.prec = 60
        expected_y = []
        expected_v = []
        for time in t:
            x = Decimal(str(time))
            decay = (-x).exp()
            expected_y.append(float(1-(1+x)*decay))
            expected_v.append(float(x*decay))
    result = solve_analytical(ModelParams(2., 1., 1.), t)
    np.testing.assert_allclose(result.y, expected_y, rtol=1e-12, atol=1e-16)
    np.testing.assert_allclose(result.v, expected_v, rtol=1e-12, atol=1e-16)
    assert result.y[0] == result.v[0] == 0
    assert result.method == "analytical"


def test_small_times_preserve_nonzero_response():
    t = np.array([0., 1e-12, 1e-8, .000999, .001, .001001])
    with localcontext() as ctx:
        ctx.prec = 80
        expected = [float(1-(1+Decimal(str(x)))*(-Decimal(str(x))).exp()) for x in t]
    result = solve_analytical(ModelParams(2., 1., 1.), t)
    np.testing.assert_allclose(result.y, expected, rtol=1e-12, atol=0)


@pytest.mark.parametrize("sigma,gain", [(.5, 1.), (1., 3.), (2., .5)])
def test_initial_state_limit_monotonicity_and_differential_equation(sigma, gain):
    a0 = sigma**2
    model = ModelParams(2*sigma, a0, gain*a0)
    t = np.concatenate(([0.], np.geomspace(1e-6/sigma, 1000/sigma, 200)))
    result = solve_analytical(model, t)
    assert result.y[0] == result.v[0] == 0
    assert result.y[-1] == pytest.approx(gain)
    assert result.v[-1] == 0
    assert np.all(np.diff(result.y) >= -1e-14)
    assert np.all(result.v >= 0)
    # Independent second derivative of the closed form satisfies the ODE.
    acceleration = model.b0*(1-sigma*t)*np.exp(-sigma*t)
    np.testing.assert_allclose(acceleration+model.a1*result.v+model.a0*result.y, model.b0, rtol=1e-13)


def test_gain_scaling_and_array_ownership_on_irregular_grid():
    t = np.array([0., .07, .4, 1.3, 5.])
    original = t.copy()
    base = solve_analytical(ModelParams(2., 1., 1.), t)
    scaled = solve_analytical(ModelParams(2., 1., 4.), t)
    np.testing.assert_allclose(scaled.y, 4*base.y)
    np.testing.assert_allclose(scaled.v, 4*base.v)
    np.testing.assert_array_equal(t, original)
    assert not np.shares_memory(t, base.t)


@pytest.mark.parametrize("a1", [1., 3.])
def test_other_cases_are_explicitly_deferred(a1):
    with pytest.raises(NotImplementedError, match="Case 2 only"):
        solve_analytical(ModelParams(a1, 1., 1.), np.array([0., 1.]))


@pytest.mark.parametrize("t", [
    [0., 1.], np.array([0, 1]), np.array([0., 1.], dtype=np.float32),
    np.array([]), np.array([0.]), np.array([[0., 1.]]),
    np.array([1., 2.]), np.array([0., 1., 1.]), np.array([0., -1.]),
    np.array([0., np.inf]), np.array([0., np.nan]),
])
def test_invalid_time_grid_is_rejected(t):
    with pytest.raises(ValueError):
        solve_analytical(ModelParams(2., 1., 1.), t)


def test_unrepresentable_gain_is_a_calculation_error():
    with pytest.raises(FloatingPointError, match="float64"):
        solve_analytical(ModelParams(2e-150, 1e-300, 1e308), np.array([0., 1.]))


def test_critical_roundoff_band_uses_same_branch_as_classification():
    result = solve_analytical(ModelParams(np.nextafter(2., 0.), 1., 1.), np.array([0., 1.]))
    assert result.y[1] == pytest.approx(1-2/np.e)
