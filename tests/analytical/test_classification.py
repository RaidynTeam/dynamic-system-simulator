import numpy as np
import pytest

from dss.analytical import classify_case, classify_roots
from dss.contracts import ModelParams


@pytest.mark.parametrize("a1,root_class,case", [
    (1., "complex_conjugate", 1),
    (2., "repeated_real", 2),
    (3., "distinct_real", 3),
])
@pytest.mark.parametrize("b0", [.5, 1., 10.])
def test_handout_examples(a1, root_class, case, b0):
    model = ModelParams(a1=a1, a0=1., b0=b0)
    assert classify_roots(model) == root_class
    assert classify_case(model) == case


def test_roundoff_near_critical_uses_repeated_branch():
    for a1 in (np.nextafter(2., 0.), np.nextafter(2., np.inf)):
        assert classify_case(ModelParams(a1, 1., 1.)) == 2


@pytest.mark.parametrize("a1,case", [(2.-1e-6, 1), (2.+1e-6, 3)])
def test_resolvable_distance_from_critical_preserves_sign(a1, case):
    assert classify_case(ModelParams(a1, 1., 1.)) == case


@pytest.mark.parametrize("a1,a0,case", [
    (1e308, 1., 3),
    (1., 1e308, 1),
    (2e-150, 1e-300, 2),
    (1e-150, 1e-300, 1),
    (3e-150, 1e-300, 3),
])
def test_extreme_scales_do_not_overflow_or_use_absolute_tolerance(a1, a0, case):
    assert classify_case(ModelParams(a1, a0, 1.)) == case
