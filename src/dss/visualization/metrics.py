"""Absolute position-error metrics against a reference response.

The shared contract fixes both formulas and restricts them to y:

    max_abs = max(abs(candidate.y - reference.y))
    rmse    = sqrt(mean((candidate.y - reference.y) ** 2))

The velocity error is deliberately not folded in. A single number mixing a
position and a velocity error would describe neither, and the handout compares
the step response y(t). No percentage error is offered either: the response
starts at y(0) = 0, so a relative error would divide by zero at the first
sample and be meaningless near it.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from dss.contracts import ErrorMetrics, Response, validate_response


def error_signal(reference: Response, candidate: Response) -> NDArray[np.float64]:
    """Return abs(candidate.y - reference.y) on the one shared time grid.

    Both responses must carry exactly the same samples. Comparing different
    grids would require interpolation, which would invent values that neither
    solver produced, so it raises instead.
    """
    for name, response in (("reference", reference), ("candidate", candidate)):
        if not isinstance(response, Response):
            raise ValueError(f"{name} must be a shared Response object")
        validate_response(response)
    if not np.array_equal(reference.t, candidate.t):
        raise ValueError(
            "reference and candidate must share one time grid; "
            "the error is never computed across interpolated samples"
        )

    difference = np.abs(candidate.y - reference.y)
    if not np.isfinite(difference).all():
        # Both inputs are finite, but their difference can still leave the
        # float64 range at the extremes of the contract.
        raise FloatingPointError("Error signal exceeded the float64 range")
    return difference


def compute_error(reference: Response, candidate: Response) -> ErrorMetrics:
    """Measure one candidate against the reference, position only."""
    difference = error_signal(reference, candidate)
    largest = float(np.max(difference))
    if largest == 0.0:
        # Identical signals; dividing by the scale below would be 0/0.
        return ErrorMetrics(max_abs=0.0, rmse=0.0)

    # Factor the largest deviation out before squaring. The contract's
    # mean(d**2) overflows float64 once d passes about 1e154, and this form
    # returns the same value without that ceiling.
    normalised = difference / largest
    rmse = largest * float(np.sqrt(np.mean(normalised * normalised)))
    return ErrorMetrics(max_abs=largest, rmse=rmse)
