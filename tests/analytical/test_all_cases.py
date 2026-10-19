"""Independent high-precision references and physical invariants for M3."""
from decimal import Decimal, localcontext

import numpy as np
import pytest

from dss.analytical import solve_analytical
from dss.contracts import ModelParams


def decimal_sin_cos(x):
    sine, cosine = x, Decimal(1)
    sin_term, cos_term = x, Decimal(1)
    for n in range(1, 100):
        sin_term *= -x*x / (2*n*(2*n+1))
        cos_term *= -x*x / ((2*n-1)*(2*n))
        sine += sin_term
        cosine += cos_term
    return sine, cosine


def reference(model, times):
    """Handout forms evaluated at 80 decimal digits; no production helpers."""
    with localcontext() as ctx:
        ctx.prec = 80
        a1, a0, b0 = (Decimal(str(x)) for x in (model.a1, model.a0, model.b0))
        sigma, gain = a1/2, b0/a0
        discriminant = sigma*sigma-a0
        ys, vs = [], []
        for time in times:
            t = Decimal(str(time))
            if t == 0:
                ys.append(0.)
                vs.append(0.)
                continue
            if discriminant < 0:
                omega = (-discriminant).sqrt()
                sine, cosine = decimal_sin_cos(omega*t)
                decay = (-sigma*t).exp()
                y = gain*(1-decay*(cosine+sigma/omega*sine))
                v = b0/omega*decay*sine
            elif discriminant > 0:
                delta = discriminant.sqrt()
                s1, s2 = -sigma+delta, -sigma-delta
                e1, e2 = (s1*t).exp(), (s2*t).exp()
                y = gain*(1+s2/(s1-s2)*e1+s1/(s2-s1)*e2)
                v = b0/(s1-s2)*(e1-e2)
            else:
                decay = (-sigma*t).exp()
                y = gain*(1-(1+sigma*t)*decay)
                v = gain*sigma*sigma*t*decay
            ys.append(float(y))
            vs.append(float(v))
        return np.array(ys), np.array(vs)


@pytest.mark.parametrize("a1", [1., 2., 3.])
@pytest.mark.parametrize("b0", [.5, 1., 4.])
def test_three_handout_cases_against_high_precision_reference(a1, b0):
    model = ModelParams(a1, 1., b0)
    t = np.array([0., 1e-12, 1e-8, .0001, .003, .009, .01, .1, .7, 2., 10.])
    result = solve_analytical(model, t)
    y, v = reference(model, t)
    np.testing.assert_allclose(result.y, y, rtol=2e-12, atol=0)
    np.testing.assert_allclose(result.v, v, rtol=2e-13, atol=0)
    assert result.y[0] == result.v[0] == 0
    np.testing.assert_array_equal(result.t, t)


@pytest.mark.parametrize("a1", [2.-1e-8, 2.+1e-8, 2.-1e-12, 2.+1e-12])
def test_near_critical_but_outside_tolerance_matches_own_exact_model(a1):
    model = ModelParams(a1, 1., 1.)
    t = np.array([0., 1e-8, .01, .1, 1., 10.])
    result = solve_analytical(model, t)
    y, v = reference(model, t)
    np.testing.assert_allclose(result.y, y, rtol=2e-12, atol=0)
    np.testing.assert_allclose(result.v, v, rtol=2e-13, atol=0)
    critical = solve_analytical(ModelParams(2., 1., 1.), t)
    np.testing.assert_allclose(result.y, critical.y, rtol=1e-8, atol=1e-15)


def test_separated_roots_keep_slow_mode_and_avoid_hyperbolic_overflow():
    model = ModelParams(1e8, 1., 1.)
    t = np.array([0., 1e-12, 1e-8, 1., 1e8, 1e10])
    result = solve_analytical(model, t)
    y, v = reference(model, t)
    np.testing.assert_allclose(result.y, y, rtol=2e-12, atol=0)
    np.testing.assert_allclose(result.v, v, rtol=2e-12, atol=1e-60)
    assert result.y[-1] == pytest.approx(1.)


@pytest.mark.parametrize("a1", [1., 2., 3.])
def test_derivative_consistency_and_ode_residual(a1):
    model = ModelParams(a1, 1., 2.)
    for time in [.05, .5, 2., 5.]:
        h = .001
        t = np.array([0., time-2*h, time-h, time, time+h, time+2*h])
        r = solve_analytical(model, t)
        y_prime = (r.y[1]-8*r.y[2]+8*r.y[4]-r.y[5])/(12*h)
        v_prime = (r.v[1]-8*r.v[2]+8*r.v[4]-r.v[5])/(12*h)
        assert y_prime == pytest.approx(r.v[3], rel=1e-8, abs=2e-10)
        assert v_prime+a1*r.v[3]+r.y[3] == pytest.approx(model.b0, abs=2e-9)


@pytest.mark.parametrize("a1", [1., 2., 3.])
def test_steady_state_and_gain_scaling(a1):
    t = np.concatenate(([0.], np.linspace(.01, 200., 2000)))
    base = solve_analytical(ModelParams(a1, 1., 1.), t)
    scaled = solve_analytical(ModelParams(a1, 1., 3.), t)
    assert base.y[-1] == pytest.approx(1., abs=1e-12)
    assert base.v[-1] == pytest.approx(0., abs=1e-12)
    np.testing.assert_allclose(scaled.y, 3*base.y)
    np.testing.assert_allclose(scaled.v, 3*base.v)
    if a1 == 1:
        assert np.max(base.y) > 1.1  # Oscillatory overshoot is physical.
    else:
        assert np.all(np.diff(base.y) >= -1e-14)
        assert np.all(base.v >= 0)


@pytest.mark.parametrize("a1", [1., 3.])
def test_nonunit_natural_frequency(a1):
    model = ModelParams(a1*3, 9., 4.5)
    t = np.array([0., 1e-12, .01, .03, .1, .7, 2.])
    result = solve_analytical(model, t)
    y, v = reference(model, t)
    np.testing.assert_allclose(result.y, y, rtol=2e-12, atol=0)
    np.testing.assert_allclose(result.v, v, rtol=2e-13, atol=0)
