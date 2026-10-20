"""Sample curves must obey the shared contract and stay recognisably samples."""

import numpy as np
import pytest

from dss.contracts import Response, validate_response
from dss.demo_data import (
    DEMO_LABEL,
    DEMO_SAMPLES,
    DEMO_T_END,
    _base_curve,
    make_demo_responses,
)
from dss.visualization.styles import METHOD_ORDER


def test_returns_one_labelled_response_per_method_in_contract_order():
    responses = make_demo_responses()
    assert [response.method for response in responses] == list(METHOD_ORDER)
    assert all(isinstance(response, Response) for response in responses)


def test_every_response_satisfies_the_shared_validator():
    for response in make_demo_responses():
        validate_response(response)


def test_all_three_share_one_time_grid():
    responses = make_demo_responses()
    for response in responses[1:]:
        assert np.array_equal(responses[0].t, response.t)
    assert responses[0].t[0] == 0.0
    assert responses[0].t[-1] == DEMO_T_END
    assert responses[0].t.size == DEMO_SAMPLES


def test_curves_start_from_the_lab_zero_state():
    for response in make_demo_responses():
        assert response.y[0] == 0.0
        assert response.v[0] == 0.0


def test_output_is_deterministic():
    first, second = make_demo_responses(), make_demo_responses()
    for left, right in zip(first, second):
        assert left.method == right.method
        assert np.array_equal(left.y, right.y)
        assert np.array_equal(left.v, right.v)


def test_the_three_curves_are_visually_distinguishable():
    responses = {response.method: response for response in make_demo_responses()}
    reference = responses["analytical"]
    for method in ("euler", "rk4"):
        gap = np.max(np.abs(responses[method].y - reference.y))
        assert gap > 1e-3


def test_mutating_a_result_cannot_affect_a_later_call():
    first = make_demo_responses()[0]
    baseline = first.y.copy()
    first.y[:] = 0.0
    assert np.array_equal(make_demo_responses()[0].y, baseline)


def test_base_curve_v_is_the_exact_derivative_of_y():
    # Checked on a dense grid; the 0.5 s sample spacing is far too coarse for a
    # finite-difference comparison near the knee of the curve.
    t = np.linspace(0.0, DEMO_T_END, 200_001, dtype=np.float64)
    y, v = _base_curve(t)
    central = (y[2:] - y[:-2]) / (t[2:] - t[:-2])
    assert np.max(np.abs(central - v[1:-1])) < 1e-6


def test_sample_curves_rise_monotonically_towards_one():
    for response in make_demo_responses():
        assert np.all(np.diff(response.y) > 0)
        assert np.all(response.v >= 0)
        assert 0.99 < response.y[-1] < 1.0


def test_the_sample_notice_is_available_for_the_ui():
    assert DEMO_LABEL.strip()


def test_the_shape_is_not_one_of_the_handout_step_responses():
    # y = t^2/(1+t^2) decays towards 1 like 1/t^2, far slower than any
    # exponential response, so it cannot pass as a Lab 1 result.
    response = make_demo_responses()[0]
    tail = response.t[-1]
    assert 1.0 - response.y[-1] == pytest.approx(1.0 / (1.0 + tail * tail), rel=1e-9)
