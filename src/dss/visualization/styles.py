"""Qt-free method identity and figure themes for the Lab 1 comparison views.

This module is deliberately pure data: it imports neither Matplotlib nor Qt, so
the UI can read the agreed curve identity without pulling a plotting backend.
It is the single source of truth for method colors; `dss.ui.colors.METHOD_COLORS`
currently holds a second copy of the light values and Person 3 is asked to
import from here instead.

Light colors are the identities the team agreed in the UI module notes retained in the local project archive. The dark
variants are a proposal: measured against the dark card #1E293B, Exact #475569
reaches only 1.93:1 and RK4 #2563EB only 2.83:1 contrast, below the 3:1 floor for
non-text marks, so both are lightened for dark mode. Euler #FF1D8D keeps its
identity in both modes. Methods also differ in line style, so color is never the
only channel that separates them.
"""

from dataclasses import dataclass
from typing import Literal

Mode = Literal["light", "dark"]

MODES: tuple[str, ...] = ("light", "dark")

#: Drawing order; matches the shared `Method` literal in dss.contracts.
METHOD_ORDER: tuple[str, ...] = ("analytical", "euler", "rk4")

#: Legend text. The handout calls the closed-form solution "Exact", not
#: "analytical", so the internal method name is not shown to the user.
METHOD_LABELS: dict[str, str] = {
    "analytical": "Exact",
    "euler": "Euler",
    "rk4": "RK4",
}

METHOD_COLORS: dict[str, dict[str, str]] = {
    "light": {"analytical": "#475569", "euler": "#FF1D8D", "rk4": "#2563EB"},
    "dark": {"analytical": "#CBD5E1", "euler": "#FF1D8D", "rk4": "#60A5FA"},
}

# Dash patterns as (offset, on/off sequence) in points, so the second encoding
# channel is explicit and testable rather than a named style that may change.
METHOD_LINESTYLES: dict[str, object] = {
    "analytical": "solid",
    "euler": (0, (5.5, 2.5)),
    "rk4": (0, (1.2, 2.6, 6.0, 2.6)),
}

# The reference curve is drawn thickest and lowest; the dashed numerical curves
# sit above it, so the gaps in their dashes keep the reference visible when the
# three responses nearly coincide. The width gap is large on purpose: RK4 tracks
# Exact so closely that a narrower reference disappears underneath it, leaving a
# visible grey halo on both sides of the overlaying dashed curve.
METHOD_LINEWIDTHS: dict[str, float] = {"analytical": 3.2, "euler": 1.6, "rk4": 1.6}
METHOD_ZORDERS: dict[str, int] = {"analytical": 2, "euler": 4, "rk4": 3}
METHOD_MARKERS: dict[str, str | None] = {"analytical": None, "euler": "o", "rk4": "^"}


@dataclass(frozen=True)
class MethodStyle:
    """Everything one response curve needs, with no Matplotlib types involved."""

    method: str
    label: str
    color: str
    linestyle: object
    linewidth: float
    zorder: int
    marker: str | None
    markersize: float


@dataclass(frozen=True)
class FigureTheme:
    """Surrounding colors for a figure; `surface` matches the UI card color."""

    mode: str
    surface: str
    text: str
    secondary: str
    grid: str
    spine: str


FIGURE_THEMES: dict[str, FigureTheme] = {
    "light": FigureTheme(
        mode="light",
        surface="#FFFFFF",
        text="#0F172A",
        secondary="#64748B",
        grid="#E2E8F0",
        spine="#E2E8F0",
    ),
    "dark": FigureTheme(
        mode="dark",
        surface="#1E293B",
        text="#F8FAFC",
        secondary="#94A3B8",
        grid="#334155",
        spine="#475569",
    ),
}


def _check_mode(mode: str) -> str:
    if not isinstance(mode, str) or mode not in FIGURE_THEMES:
        raise ValueError("mode must be light or dark")
    return mode


def _check_method(method: str) -> str:
    if not isinstance(method, str) or method not in METHOD_ORDER:
        raise ValueError("method must be analytical, euler or rk4")
    return method


def figure_theme(mode: Mode = "light") -> FigureTheme:
    """Return the frozen palette for one UI theme."""
    return FIGURE_THEMES[_check_mode(mode)]


def method_color(method: str, mode: Mode = "light") -> str:
    """Return one curve color; light values are the team-agreed identities."""
    return METHOD_COLORS[_check_mode(mode)][_check_method(method)]


def method_style(method: str, mode: Mode = "light") -> MethodStyle:
    """Return the full identity of one method's curve."""
    _check_mode(mode)
    _check_method(method)
    return MethodStyle(
        method=method,
        label=METHOD_LABELS[method],
        color=METHOD_COLORS[mode][method],
        linestyle=METHOD_LINESTYLES[method],
        linewidth=METHOD_LINEWIDTHS[method],
        zorder=METHOD_ZORDERS[method],
        marker=METHOD_MARKERS[method],
        markersize=4.5,
    )


def plot_kwargs(method: str, mode: Mode = "light") -> dict:
    """Keyword arguments for one `Axes.plot` call, ready to splat.

    `marker` is omitted when the method draws none, and `markevery` is left to
    the caller because a sensible stride depends on the sample count.
    """
    style = method_style(method, mode)
    kwargs = {
        "label": style.label,
        "color": style.color,
        "linestyle": style.linestyle,
        "linewidth": style.linewidth,
        "zorder": style.zorder,
        "solid_capstyle": "round",
        "dash_capstyle": "round",
    }
    if style.marker is not None:
        kwargs["marker"] = style.marker
        kwargs["markersize"] = style.markersize
        kwargs["markeredgecolor"] = style.color
        kwargs["markerfacecolor"] = "none"
    return kwargs
