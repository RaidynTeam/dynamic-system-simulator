"""Classical Runge-Kutta from Word handout formulas (18)-(19)."""

import numpy as np
from numpy.typing import NDArray

from dss.contracts import ModelParams, Response
from ._common import derivative, validate_inputs


def solve_rk4(model: ModelParams, t: NDArray[np.float64]) -> Response:
    """Use four coupled y/v slopes per interval, without changing the grid."""
    validate_inputs(model, t)
    state = np.zeros((len(t), 2), dtype=np.float64)
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise", under="ignore"):
            for i in range(len(t) - 1):
                h = t[i + 1] - t[i]
                current = state[i]
                # k values are slopes; the Word document's increments are h*k.
                k1 = derivative(model, current)
                k2 = derivative(model, current + (h / 2) * k1)
                k3 = derivative(model, current + (h / 2) * k2)
                k4 = derivative(model, current + h * k3)
                state[i + 1] = current + (h / 6) * (k1 + 2*k2 + 2*k3 + k4)
    except FloatingPointError as exc:
        raise FloatingPointError("RK4 calculation overflowed; try a smaller time step") from exc
    if not np.isfinite(state).all():
        raise FloatingPointError("RK4 calculation produced non-finite values")
    return Response(t=t, y=state[:, 0], v=state[:, 1], method="rk4")
