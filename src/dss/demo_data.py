"""Deterministic development fixtures for the plot and canvas work.

These curves are **not** solver output and are **not** evidence about any
method's accuracy. They exist only so a figure, a canvas or a layout can be
exercised without running a solver, and the shared v0.2 contract requires any
UI that shows them to carry the visible `DEMO_LABEL` notice.

The shape is a rational saturating curve, not one of the handout's three
closed-form step responses, precisely so it cannot be mistaken for a real
result or become a second implementation of Person 1's formulas. The per-method
deviations are arbitrary constants chosen to make three curves visually
distinguishable; they are not error estimates and their sizes carry no claim
about which method is more accurate.

The production application does not import this module: all three real solvers
are available, so the UI has no reason to display sample data.
"""

import numpy as np
from numpy.typing import NDArray

from dss.contracts import Response

#: Wording the shared contract requires the UI to show beside these curves.
DEMO_LABEL = "Örnek veri"

DEMO_T_END = 20.0
DEMO_SAMPLES = 41  # 0.5 s spacing; small enough to read individual markers.

# Arbitrary, clearly different offsets. See the module docstring.
_DEVIATIONS: dict[str, float] = {"analytical": 0.0, "euler": 0.06, "rk4": -0.025}


def _base_curve(t: NDArray[np.float64]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """y = t^2 / (1 + t^2) and its exact derivative, so y(0) = v(0) = 0."""
    squared = t * t
    denominator = 1.0 + squared
    y = squared / denominator
    v = 2.0 * t / (denominator * denominator)
    return y, v


def make_demo_responses() -> list[Response]:
    """Three labelled sample responses on one shared, deterministic time grid.

    Returns one Response per method name in the contract's order. Every call
    rebuilds the arrays, and Response copies them, so a caller that mutates the
    result cannot affect a later call.
    """
    t = np.linspace(0.0, DEMO_T_END, DEMO_SAMPLES, dtype=np.float64)
    y, v = _base_curve(t)
    # A decaying factor keeps y(0) = v(0) = 0 and the same final value for all three.
    fade = np.exp(-t / 4.0)
    responses = []
    for method, deviation in _DEVIATIONS.items():
        scale = 1.0 + deviation * fade
        derivative = -deviation / 4.0 * fade
        responses.append(
            Response(
                t=t,
                y=y * scale,
                v=v * scale + y * derivative,
                method=method,
            )
        )
    return responses
