"""Forward Euler from formula (15) in the original Word handout."""

import numpy as np
from numpy.typing import NDArray

from dss.contracts import ModelParams, Response
from ._common import derivative, validate_inputs


def solve_euler(model: ModelParams, t: NDArray[np.float64]) -> Response:
    """Advance y and v from the same old state on each supplied interval."""
    validate_inputs(model, t)
    state = np.zeros((len(t), 2), dtype=np.float64)  # y(0) = v(0) = 0.
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise", under="ignore"):
            for i in range(len(t) - 1):
                h = t[i + 1] - t[i]
                state[i + 1] = state[i] + h * derivative(model, state[i])
    except FloatingPointError as exc:
        raise FloatingPointError("Euler calculation overflowed; try a smaller time step") from exc
    if not np.isfinite(state).all():
        raise FloatingPointError("Euler calculation produced non-finite values")
    return Response(t=t, y=state[:, 0], v=state[:, 1], method="euler")
