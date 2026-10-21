"""Lazy adapter to Person 4's APIs. Contains no plotting or metric algorithms."""

from dataclasses import dataclass
from importlib import import_module
from typing import Callable

from matplotlib.figure import Figure


class VisualizationUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class VisualizationAPI:
    build_response_figure: Callable
    build_error_figure: Callable
    compute_error: Callable
    export_figure: Callable


def load_visualization_api() -> VisualizationAPI:
    namespace = import_module("dss.visualization")
    functions = {}
    for name, module in (
        ("build_response_figure", "plots"), ("build_error_figure", "plots"),
        ("compute_error", "metrics"), ("export_figure", "export"),
    ):
        function = getattr(namespace, name, None)
        if not callable(function):
            function = getattr(import_module(f"dss.visualization.{module}"), name, None)
        if not callable(function):
            raise VisualizationUnavailable(f"Visualization API unavailable: {name} (Person 4).")
        functions[name] = function
    return VisualizationAPI(**functions)


@dataclass(frozen=True)
class PreparedResults:
    response_figure: Figure
    error_figure: Figure | None
    metrics: dict
    methods: tuple[str, ...]
    api: VisualizationAPI
    responses: tuple


def prepare_results(responses: list, api: VisualizationAPI | None = None, *, theme: str = "light") -> PreparedResults:
    """Validate genuine shared responses, then delegate all visual calculations."""
    import numpy as np
    from dss.contracts import ErrorMetrics, Response, validate_response

    if not responses:
        raise ValueError("No simulation responses were supplied.")
    for response in responses:
        if not isinstance(response, Response):
            raise ValueError("Results must use the shared Response contract.")
        validate_response(response)
    methods = tuple(response.method for response in responses)
    if len(set(methods)) != len(methods):
        raise ValueError("Each result method must be unique.")
    if any(not np.array_equal(responses[0].t, response.t) for response in responses[1:]):
        raise ValueError("Response time grids must match exactly.")
    api = api if api is not None else load_visualization_api()
    reference = next((r for r in responses if r.method == "analytical"), None)
    candidates = [r for r in responses if r.method != "analytical"]
    metrics = {}
    if reference is not None:
        for candidate in candidates:
            result = api.compute_error(reference, candidate)
            if not isinstance(result, ErrorMetrics):
                raise ValueError("Visualization must return shared ErrorMetrics objects.")
            # ErrorMetrics is frozen, but validate finite/nonnegative fields again
            # at this public boundary in case an external producer bypassed init.
            ErrorMetrics(result.max_abs, result.rmse)
            metrics[candidate.method] = result
    return _build_figures(tuple(responses), metrics, methods, api, theme)


def retheme_results(prepared: PreparedResults, theme: str) -> PreparedResults:
    """Rebuild owner-styled figures without solving or recalculating metrics."""
    return _build_figures(prepared.responses, prepared.metrics, prepared.methods, prepared.api, theme)


def _build_figures(responses, metrics, methods, api, theme) -> PreparedResults:
    reference = next((r for r in responses if r.method == "analytical"), None)
    candidates = [r for r in responses if r.method != "analytical"]
    figure = api.build_response_figure(responses, theme=theme)
    error = api.build_error_figure(reference, candidates, theme=theme) if reference is not None and candidates else None
    if not isinstance(figure, Figure) or (error is not None and not isinstance(error, Figure)):
        raise ValueError("Visualization must return Matplotlib Figure objects.")
    if error is figure:
        raise ValueError("Response and error views must use distinct Figure objects.")
    return PreparedResults(figure, error, metrics, methods, api, responses)
