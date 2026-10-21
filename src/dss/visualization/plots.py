"""Comparison figures for the Lab 1 zero-state unit-step experiment.

Every call returns a brand new Figure, so a repeated run can never draw onto
the previous one. Input Responses are only read; their arrays are never
modified, sorted or reused as the figure's own storage.
"""

from __future__ import annotations

from math import ceil

import numpy as np
from matplotlib.figure import Figure

from dss.contracts import Response, validate_response

from .figures import new_figure, style_axes
from .styles import METHOD_ORDER, Mode, plot_kwargs

#: Upper bound on markers per curve; a 1,000,000-sample grid would otherwise
#: paint a solid band of markers and hide the curve itself.
MAX_MARKERS = 40

#: The handout fixes the input to a unit step with zero initial conditions.
DEFAULT_RESPONSE_TITLE = "Unit step response comparison"

TIME_LABEL = "Time (s)"
# No physical unit: the handout never states what y measures, so inventing one
# would be a claim the assignment does not support.
OUTPUT_LABEL = "Output y(t)"


def _ordered_responses(responses) -> list[Response]:
    """Validate the comparison set and return it in a stable legend order."""
    if isinstance(responses, Response) or not isinstance(responses, (list, tuple)):
        raise ValueError("responses must be a list or tuple of Response objects")
    if not responses:
        raise ValueError("At least one response is required to draw a figure")
    for response in responses:
        if not isinstance(response, Response):
            raise ValueError("Every item must be a shared Response object")
        validate_response(response)

    methods = [response.method for response in responses]
    if len(set(methods)) != len(methods):
        raise ValueError("Each method may appear only once in one figure")

    reference = responses[0].t
    for response in responses[1:]:
        if not np.array_equal(reference, response.t):
            raise ValueError(
                "All responses must share one time grid; "
                "this figure never interpolates between different grids"
            )
    # Canonical order keeps the legend identical across runs, whatever order the
    # user selected the methods in. Visual stacking is set by zorder, not here.
    return sorted(responses, key=lambda response: METHOD_ORDER.index(response.method))


def _marker_stride(sample_count: int) -> int:
    return max(1, ceil(sample_count / MAX_MARKERS))


def build_response_figure(
    responses: list[Response],
    *,
    theme: Mode = "light",
    title: str | None = None,
) -> Figure:
    """Draw y(t) for every supplied method on one shared time axis.

    `theme` and `title` are keyword-only with defaults, so the shared contract
    call `build_response_figure(responses)` keeps working unchanged.
    """
    if title is not None and (not isinstance(title, str) or not title.strip()):
        raise ValueError("title must be a non-empty string when given")

    ordered = _ordered_responses(responses)
    figure = new_figure(theme)
    axes = figure.add_subplot()

    stride = _marker_stride(ordered[0].t.size)
    for response in ordered:
        axes.plot(
            response.t,
            response.y,
            markevery=stride,
            **plot_kwargs(response.method, theme),
        )

    axes.set_title(title if title is not None else DEFAULT_RESPONSE_TITLE)
    axes.set_xlabel(TIME_LABEL)
    axes.set_ylabel(OUTPUT_LABEL)
    # The step starts at t=0; a default 5% margin would show empty space there.
    axes.set_xlim(ordered[0].t[0], ordered[0].t[-1])
    axes.legend(loc="best")
    style_axes(axes, theme)
    return figure
