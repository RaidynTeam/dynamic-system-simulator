"""Characteristic-root classification for the three assignment cases."""

from math import sqrt
from typing import Literal

import numpy as np

from dss.contracts import ModelParams, validate_model

RootClass = Literal["complex_conjugate", "repeated_real", "distinct_real"]
# Relative tolerance after scaling both discriminant terms to at most one.
CRITICAL_RTOL = 64 * np.finfo(np.float64).eps


def classify_roots(model: ModelParams) -> RootClass:
    """Classify a1**2 - 4*a0 without overflowing those products.

    Values within CRITICAL_RTOL of critical damping use the repeated-root
    branch. This is a floating-point convention, not exact symbolic equality.
    """
    validate_model(model)
    twice_natural_frequency = 2 * sqrt(model.a0)
    scale = max(model.a1, twice_natural_frequency)
    discriminant = (model.a1 / scale) ** 2 - (twice_natural_frequency / scale) ** 2
    if abs(discriminant) <= CRITICAL_RTOL:
        return "repeated_real"
    if discriminant < 0:
        return "complex_conjugate"
    return "distinct_real"


def classify_case(model: ModelParams) -> Literal[1, 2, 3]:
    """Return the Case number used in the lab handout."""
    roots = classify_roots(model)
    if roots == "complex_conjugate":
        return 1
    if roots == "repeated_real":
        return 2
    return 3
