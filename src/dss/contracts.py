"""Shared Lab 1 data contracts for a zero-state unit-step response."""

from dataclasses import dataclass
from math import isfinite
from numbers import Real
from typing import Literal

import numpy as np
from numpy.typing import NDArray

Method = Literal["analytical", "euler", "rk4"]


def _finite_real(name: str, value: float) -> None:
    try:
        valid = isinstance(value, Real) and not isinstance(value, (bool, np.bool_)) and isfinite(value)
    except (OverflowError, TypeError, ValueError):
        valid = False
    if not valid:
        raise ValueError(f"{name} must be a finite real number")


@dataclass(frozen=True)
class ModelParams:
    """y'' + a1*y' + a0*y = b0, with y(0) = y'(0) = 0."""

    a1: float
    a0: float
    b0: float

    def __post_init__(self) -> None:
        validate_model(self)


@dataclass(frozen=True)
class SimulationConfig:
    """Time interval in seconds; Lab 1 always starts at zero."""

    t0: float
    t_end: float
    dt: float

    def __post_init__(self) -> None:
        validate_config(self)


@dataclass(frozen=True)
class Response:
    """Owns copies of float64 samples; array contents remain mutable."""

    t: NDArray[np.float64]
    y: NDArray[np.float64]
    v: NDArray[np.float64]
    method: Method

    def __post_init__(self) -> None:
        validate_response(self)
        for name in ("t", "y", "v"):
            object.__setattr__(self, name, getattr(self, name).copy())


@dataclass(frozen=True)
class ErrorMetrics:
    """Absolute position-error metrics, calculated by visualization."""

    max_abs: float
    rmse: float

    def __post_init__(self) -> None:
        for name in ("max_abs", "rmse"):
            value = getattr(self, name)
            _finite_real(name, value)
            if value < 0:
                raise ValueError(f"{name} must be nonnegative")


def validate_model(model: ModelParams) -> None:
    """The assignment requires positive, finite a1, a0 and b0."""
    for name in ("a1", "a0", "b0"):
        value = getattr(model, name)
        _finite_real(name, value)
        if value <= 0:
            raise ValueError(f"{name} must be positive")


def validate_config(config: SimulationConfig) -> None:
    for name in ("t0", "t_end", "dt"):
        _finite_real(name, getattr(config, name))
    if config.t0 != 0:
        raise ValueError("t0 must be zero for the Lab 1 unit step")
    if config.t_end <= config.t0:
        raise ValueError("t_end must be greater than t0")
    if config.dt <= 0:
        raise ValueError("dt must be positive")


def validate_response(response: Response) -> None:
    for name in ("t", "y", "v"):
        samples = getattr(response, name)
        if not isinstance(samples, np.ndarray) or samples.dtype != np.dtype(np.float64):
            raise ValueError(f"{name} must be a float64 NumPy array")
        if samples.ndim != 1 or samples.size < 2:
            raise ValueError(f"{name} must be one-dimensional with at least two samples")
        if not np.isfinite(samples).all():
            raise ValueError(f"{name} must contain only finite samples")
    if not (response.t.shape == response.y.shape == response.v.shape):
        raise ValueError("t, y and v must have matching shapes")
    if response.t[0] != 0 or not np.all(response.t[1:] > response.t[:-1]):
        raise ValueError("t must start at zero and be strictly increasing")
    if not isinstance(response.method, str) or response.method not in ("analytical", "euler", "rk4"):
        raise ValueError("method must be analytical, euler or rk4")
