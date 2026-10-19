"""Exact zero-state step response; M2 implements critical damping only."""

import numpy as np
from numpy.typing import NDArray

from dss.contracts import ModelParams, Response, validate_model
from .classification import classify_case


def solve_analytical(model: ModelParams, t: NDArray[np.float64]) -> Response:
    """Evaluate handout (9) and its derivative on the supplied time grid.

    Cases 1 and 3 are intentionally deferred to M3. Values in the critical
    classification tolerance band use the repeated-root approximation.
    """
    validate_model(model)
    if not isinstance(t, np.ndarray) or t.dtype != np.dtype(np.float64):
        raise ValueError("t must be a float64 NumPy array")
    if t.ndim != 1 or t.size < 2 or not np.isfinite(t).all():
        raise ValueError("t must be one-dimensional with at least two finite samples")
    if t[0] != 0 or not np.all(t[1:] > t[:-1]):
        raise ValueError("t must start at zero and be strictly increasing")
    if classify_case(model) != 2:
        raise NotImplementedError("M2 supports Case 2 only; Cases 1 and 3 are planned for M3")

    try:
        with np.errstate(over="raise", invalid="raise", divide="raise", under="ignore"):
            sigma = np.float64(model.a1) / 2
            gain = np.float64(model.b0) / np.float64(model.a0)
            x = sigma * t
            decay = np.exp(-x)
            # expm1 avoids subtracting exp(-x) from one. Near zero, a
            # series also avoids cancellation between two terms of size x.
            step = -np.expm1(-x) - x * decay
            small = x < 1e-3
            z = x[small]
            step[small] = z * z * (
                .5 + z * (-1/3 + z * (1/8 + z * (-1/30 + z * (
                    1/144 + z * (-1/840 + z/5760)
                ))))
            )
            y = gain * step
            v = gain * sigma * x * decay
    except FloatingPointError as exc:
        raise FloatingPointError("Analytical response exceeded the float64 calculation range") from exc
    if not np.isfinite(y).all() or not np.isfinite(v).all():
        raise FloatingPointError("Analytical response contains non-finite samples")
    return Response(t=t, y=y, v=v, method="analytical")
