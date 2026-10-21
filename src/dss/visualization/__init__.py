"""Person 4: Qt-free figures, error metrics and export for Lab 1.

M1 provides the shared method identity, the figure themes and the Qt-free
Figure factory; M2 adds `build_response_figure`. `build_error_figure`,
`compute_error` and `export_figure` belong to M3-M4 and are deliberately
**not** exported yet, so `dss.ui.presentation.load_visualization_api` still
reports the real state instead of a half-working API.
"""

from .figures import (
    DEFAULT_DPI,
    DEFAULT_SIZE,
    apply_figure_theme,
    new_figure,
    style_axes,
)
from .plots import (
    DEFAULT_RESPONSE_TITLE,
    MAX_MARKERS,
    OUTPUT_LABEL,
    TIME_LABEL,
    build_response_figure,
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
    "DEFAULT_RESPONSE_TITLE",
    "DEFAULT_SIZE",
    "FIGURE_THEMES",
    "FigureTheme",
    "MAX_MARKERS",
    "METHOD_COLORS",
    "METHOD_LABELS",
    "METHOD_LINESTYLES",
    "METHOD_ORDER",
    "MODES",
    "MethodStyle",
    "OUTPUT_LABEL",
    "TIME_LABEL",
    "apply_figure_theme",
    "build_response_figure",
    "figure_theme",
    "method_color",
    "method_style",
    "new_figure",
    "plot_kwargs",
    "style_axes",
]
