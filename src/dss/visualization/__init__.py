"""Person 4: Qt-free figures, error metrics and export for Lab 1.

M1 provides the shared method identity, the figure themes and the Qt-free
Figure factory. `build_response_figure`, `build_error_figure`, `compute_error`
and `export_figure` belong to M2-M4 and are deliberately **not** exported yet,
so `dss.ui.presentation.load_visualization_api` still reports the real state
instead of a half-working API.
"""

from .figures import (
    DEFAULT_DPI,
    DEFAULT_SIZE,
    apply_figure_theme,
    new_figure,
    style_axes,
)
from .styles import (
    FIGURE_THEMES,
    METHOD_COLORS,
    METHOD_LABELS,
    METHOD_LINESTYLES,
    METHOD_ORDER,
    MODES,
    FigureTheme,
    MethodStyle,
    figure_theme,
    method_color,
    method_style,
    plot_kwargs,
)

__all__ = [
    "DEFAULT_DPI",
    "DEFAULT_SIZE",
    "FIGURE_THEMES",
    "FigureTheme",
    "METHOD_COLORS",
    "METHOD_LABELS",
    "METHOD_LINESTYLES",
    "METHOD_ORDER",
    "MODES",
    "MethodStyle",
    "apply_figure_theme",
    "figure_theme",
    "method_color",
    "method_style",
    "new_figure",
    "plot_kwargs",
    "style_axes",
]
