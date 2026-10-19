"""The same lab equation and input checks for Euler and RK4."""

import numpy as np

from dss.contracts import validate_model


def validate_inputs(model, t):
    validate_model(model)
    if not isinstance(t, np.ndarray) or t.dtype != np.dtype(np.float64):
        raise ValueError("t must be a float64 NumPy array")
    if t.ndim != 1 or t.size < 2 or not np.isfinite(t).all():
        raise ValueError("t must be one-dimensional with at least two finite samples")
    if t[0] != 0 or not np.all(t[1:] > t[:-1]):
        raise ValueError("t must start at zero and be strictly increasing")


def derivative(model, state):
    """Word (12): state = [y, v], with v = y' and unit input x = 1."""
    y, v = state
    return np.array([v, model.b0 - model.a1 * v - model.a0 * y], dtype=np.float64)
