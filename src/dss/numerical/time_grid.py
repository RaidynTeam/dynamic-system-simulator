"""Shared time samples for comparing the Lab 1 solvers."""

from math import floor, isclose, isfinite

import numpy as np
from numpy.typing import NDArray

from dss.contracts import SimulationConfig, validate_config

MAX_SAMPLES = 1_000_000  # Memory limit chosen by the team, not the handout.


def make_time_grid(config: SimulationConfig) -> NDArray[np.float64]:
    """Include zero and t_end, shortening only the final step if necessary."""
    validate_config(config)
    end, dt = float(config.t_end), float(config.dt)
    step_count = end / dt
    if not isfinite(step_count) or step_count > MAX_SAMPLES:
        raise ValueError("Time grid exceeds 1,000,000 samples")

    full_steps = floor(step_count)
    # Multiplication avoids accumulating roundoff through repeated additions.
    last = full_steps * dt
    reaches_end = isclose(last, end, rel_tol=8 * np.finfo(np.float64).eps, abs_tol=0)
    sample_count = full_steps + 1 + (not reaches_end)
    if sample_count > MAX_SAMPLES:
        raise ValueError("Time grid exceeds 1,000,000 samples")

    t = np.arange(full_steps + 1, dtype=np.float64) * dt
    if reaches_end:
        t[-1] = end
    else:
        t = np.append(t, end)
    if not np.all(t[1:] > t[:-1]):
        raise ValueError("Time step is too small to produce distinct samples")
    return t
