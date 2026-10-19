"""Exact zero-state unit-step responses for all three Lab 1 cases."""

import numpy as np
from numpy.typing import NDArray

from dss.contracts import ModelParams, Response, validate_model
from .classification import classify_case


def _critical(t, gain, sigma):
    x = sigma * t
    decay = np.exp(-x)
    y = gain * (-np.expm1(-x) - x * decay)
    v = gain * sigma * x * decay
    return y, v


def _underdamped(model, t, gain, sigma):
    natural = np.sqrt(model.a0)
    ratio = sigma / natural
    omega = natural * np.sqrt((1 - ratio) * (1 + ratio))
    x, angle = sigma * t, omega * t
    decay = np.exp(-x)
    # sinc handles sin(angle)/angle continuously near critical damping.
    sine_ratio = np.sinc(angle / np.pi)
    y = gain * (-np.expm1(-x) + decay * (
        2 * np.sin(angle / 2)**2 - x * sine_ratio
    ))
    v = model.b0 * t * decay * sine_ratio
    return y, v


def _overdamped(model, t, gain, sigma):
    ratio = np.sqrt(model.a0) / sigma
    delta = sigma * np.sqrt((1 - ratio) * (1 + ratio))
    # The product of roots is a0: avoid cancellation in -sigma + delta.
    slow = -model.a0 / (sigma + delta)
    gap = 2 * delta
    decay = np.exp(slow * t)
    # Factoring out the slow exponential avoids exp(-sigma*t)*cosh(delta*t).
    exponential_difference = -np.expm1(-gap * t) / gap
    y = gain * (-np.expm1(slow * t) + slow * decay * exponential_difference)
    v = model.b0 * decay * exponential_difference
    return y, v


def _initial_series(model, t):
    """Evaluate the ODE's power series without subtracting near-equal terms."""
    a = model.a1 * t
    b = (np.sqrt(model.a0) * t)**2
    previous = np.zeros_like(t)  # n=1 contribution
    current = np.full_like(t, .5)  # n=2 contribution, after factoring b0*t²
    position = current.copy()
    velocity = 2 * current
    for n in range(3, 13):
        term = -(a * (n - 1) * current + b * previous) / (n * (n - 1))
        position += term
        velocity += n * term
        previous, current = current, term
    return model.b0 * t * t * position, model.b0 * t * velocity


def solve_analytical(model: ModelParams, t: NDArray[np.float64]) -> Response:
    """Evaluate handout (8)–(10) and y' on a common supplied time grid.

    The critical classification tolerance band uses the repeated-root
    approximation. Extreme float64 calculation overflow raises an explicit
    FloatingPointError instead of returning invalid curves.
    """
    validate_model(model)
    if not isinstance(t, np.ndarray) or t.dtype != np.dtype(np.float64):
        raise ValueError("t must be a float64 NumPy array")
    if t.ndim != 1 or t.size < 2 or not np.isfinite(t).all():
        raise ValueError("t must be one-dimensional with at least two finite samples")
    if t[0] != 0 or not np.all(t[1:] > t[:-1]):
        raise ValueError("t must start at zero and be strictly increasing")
    case = classify_case(model)
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise", under="ignore"):
            sigma = np.float64(model.a1) / 2
            gain = np.float64(model.b0) / np.float64(model.a0)
            if case == 1:
                y, v = _underdamped(model, t, gain, sigma)
            elif case == 2:
                y, v = _critical(t, gain, sigma)
            else:
                y, v = _overdamped(model, t, gain, sigma)
            # Both dimensionless coefficients are small in this interval.
            small = t < .01 / max(model.a1, np.sqrt(model.a0))
            y[small], v[small] = _initial_series(model, t[small])
    except FloatingPointError as exc:
        raise FloatingPointError("Analytical response exceeded the float64 calculation range") from exc
    if not np.isfinite(y).all() or not np.isfinite(v).all():
        raise FloatingPointError("Analytical response contains non-finite samples")
    return Response(t=t, y=y, v=v, method="analytical")
