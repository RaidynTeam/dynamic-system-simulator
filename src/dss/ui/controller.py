"""Real solver orchestration, independent of Qt and visualization."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dss.contracts import ModelParams, Response, SimulationConfig


M1_STATUS = (
    "Run-to-plot is not connected yet. No results have been calculated."
)

_SOLVERS = {
    "analytical": ("dss.analytical", "solve_analytical"),
    "euler": ("dss.numerical", "solve_euler"),
    "rk4": ("dss.numerical", "solve_rk4"),
}


def run_simulation(
    model: ModelParams, config: SimulationConfig, methods: tuple[str, ...]
) -> list[Response]:
    """Validate, build one grid and call only selected solvers in order.

    Imports occur at execution time, so opening the UI needs no solver modules.
    Exceptions propagate unchanged; a failed run never returns partial results.
    The UI Run action remains separate until M4B.
    """
    from importlib import import_module

    import numpy as np
    from dss.contracts import (
        ModelParams, Response, SimulationConfig,
        validate_config, validate_model, validate_response,
    )

    if not isinstance(model, ModelParams):
        raise ValueError("model must be a shared ModelParams object.")
    if not isinstance(config, SimulationConfig):
        raise ValueError("config must be a shared SimulationConfig object.")
    validate_model(model)
    validate_config(config)
    if not isinstance(methods, (tuple, list)):
        raise ValueError("methods must be a tuple or list of method names.")
    methods = tuple(methods)
    if not methods:
        raise ValueError("Select at least one method.")
    if any(not isinstance(method, str) or method not in _SOLVERS for method in methods):
        raise ValueError("Unknown simulation method; choose analytical, euler or rk4.")
    if len(set(methods)) != len(methods):
        raise ValueError("Select distinct methods; duplicates are not allowed.")

    numerical = import_module("dss.numerical")
    t = numerical.make_time_grid(config)
    responses = []
    for method in methods:
        module_name, function_name = _SOLVERS[method]
        solver = getattr(import_module(module_name), function_name)
        response = solver(model, t)
        if not isinstance(response, Response):
            raise ValueError(f"{method} must return a shared Response object.")
        validate_response(response)
        if response.method != method or not np.array_equal(response.t, t):
            raise ValueError(f"{method} returned a different method or time grid.")
        responses.append(response)
    return responses
