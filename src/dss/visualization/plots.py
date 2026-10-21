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
from .metrics import error_signal
from .styles import METHOD_LABELS, METHOD_ORDER, Mode, plot_kwargs

#: Upper bound on markers per curve; a 1,000,000-sample grid would otherwise
#: paint a solid band of markers and hide the curve itself.
MAX_MARKERS = 40

#: The handout fixes the input to a unit step with zero initial conditions.
DEFAULT_RESPONSE_TITLE = "Unit step response comparison"
DEFAULT_ERROR_TITLE_TEMPLATE = "Absolute error against the {reference} response"

TIME_LABEL = "Time (s)"
# No physical unit: the handout never states what y measures, so inventing one
# would be a claim the assignment does not support.
OUTPUT_LABEL = "Output y(t)"
ERROR_LABEL_TEMPLATE = "Absolute error vs {reference}"

#: The error axis is linear by default. See build_error_figure on zeros.
ERROR_SCALES = ("linear", "log")


def _check_title(title) -> None:
    if title is not None and (not isinstance(title, str) or not title.strip()):
        raise ValueError("title must be a non-empty string when given")


def _validated(response, name: str) -> Response:
    if not isinstance(response, Response):
        raise ValueError(f"{name} must be a shared Response object")
    validate_response(response)
    return response


def _as_response_list(responses, name: str) -> list[Response]:
    if isinstance(responses, Response) or not isinstance(responses, (list, tuple)):
        raise ValueError(f"{name} must be a list or tuple of Response objects")
    if not responses:
        raise ValueError(f"At least one {name} entry is required to draw a figure")
    return [_validated(response, f"Every {name} item") for response in responses]


def _reject_repeats(methods) -> None:
    methods = list(methods)
    if len(set(methods)) != len(methods):
        raise ValueError("Each method may appear only once in one figure")


def _by_method(responses: list[Response]) -> list[Response]:
    # Canonical order keeps the legend identical across runs, whatever order the
    # user selected the methods in. Visual stacking is set by zorder, not here.
    return sorted(responses, key=lambda response: METHOD_ORDER.index(response.method))


def _ordered_responses(responses) -> list[Response]:
    """Validate the comparison set and return it in a stable legend order."""
    validated = _as_response_list(responses, "responses")
    _reject_repeats(response.method for response in validated)

    reference = validated[0].t
    for response in validated[1:]:
        if not np.array_equal(reference, response.t):
            raise ValueError(
                "All responses must share one time grid; "
                "this figure never interpolates between different grids"
            )
    return _by_method(validated)


def _marker_stride(sample_count: int) -> int:
    return max(1, ceil(sample_count / MAX_MARKERS))


def _finish(axes, *, theme, title, ylabel, t) -> None:
    axes.set_title(title)
    axes.set_xlabel(TIME_LABEL)
    axes.set_ylabel(ylabel)
    # The step starts at t=0; a default 5% margin would show empty space there.
    axes.set_xlim(t[0], t[-1])
    axes.legend(loc="best")
    style_axes(axes, theme)


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
    _check_title(title)
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

    _finish(
        axes,
        theme=theme,
        title=title if title is not None else DEFAULT_RESPONSE_TITLE,
        ylabel=OUTPUT_LABEL,
        t=ordered[0].t,
    )
    return figure


def build_error_figure(
    reference: Response,
    candidates: list[Response],
    *,
    theme: Mode = "light",
    title: str | None = None,
    scale: str = "linear",
) -> Figure:
    """Draw abs(candidate.y - reference.y) for every candidate.

    The reference itself is not drawn: its error against itself is zero by
    definition and a flat line at zero would only add legend noise.

    `scale` is linear by default, as the guide requires. A log axis cannot
    place a non-positive value, and the first sample is always exactly zero
    because every solver starts from the same y(0) = 0. Those samples are
    masked, so the curve is simply interrupted there: no substitute floor value
    is invented, and no segment is drawn towards a point that is not on the
    axis. The underlying zeros stay in the line's data. Use the linear default
    unless the orders of magnitude between methods matter more than seeing
    every sample.
    """
    _check_title(title)
    if scale not in ERROR_SCALES:
        raise ValueError("scale must be linear or log")

    base = _validated(reference, "reference")
    ordered = _by_method(_as_response_list(candidates, "candidates"))
    _reject_repeats([base.method] + [response.method for response in ordered])

    figure = new_figure(theme)
    axes = figure.add_subplot()

    stride = _marker_stride(base.t.size)
    for candidate in ordered:
        # error_signal re-checks the shared grid and rejects interpolation.
        signal = error_signal(base, candidate)
        if scale == "log":
            # Masking breaks the curve at the zeros instead of drawing a
            # segment towards a point the axis cannot show.
            signal = np.ma.masked_less_equal(signal, 0.0)
        axes.plot(
            base.t,
            signal,
            markevery=stride,
            **plot_kwargs(candidate.method, theme),
        )

    reference_label = METHOD_LABELS[base.method]
    if scale == "log":
        axes.set_yscale("log")
    _finish(
        axes,
        theme=theme,
        title=(
            title
            if title is not None
            else DEFAULT_ERROR_TITLE_TEMPLATE.format(reference=reference_label)
        ),
        ylabel=ERROR_LABEL_TEMPLATE.format(reference=reference_label),
        t=base.t,
    )
    return figure
