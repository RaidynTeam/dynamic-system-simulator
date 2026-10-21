"""Person 4: Qt-free figures, error metrics and export for Lab 1.

M1 provides the shared method identity, the figure themes and the Qt-free
Figure factory; M2 adds `build_response_figure`; M3 adds `compute_error`
and `build_error_figure`. `export_figure` belongs to M4 and is deliberately
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
from .metrics import compute_error, error_signal
from .plots import (
    DEFAULT_ERROR_TITLE_TEMPLATE,
    DEFAULT_RESPONSE_TITLE,
    ERROR_LABEL_TEMPLATE,
    ERROR_SCALES,
    MAX_MARKERS,
    OUTPUT_LABEL,
    TIME_LABEL,
    build_error_figure,
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
    "DEFAULT_ERROR_TITLE_TEMPLATE",
    "DEFAULT_RESPONSE_TITLE",
    "DEFAULT_SIZE",
    "ERROR_LABEL_TEMPLATE",
    "ERROR_SCALES",
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
    "build_error_figure",
    "build_response_figure",
    "compute_error",
    "error_signal",
    "figure_theme",
    "method_color",
    "method_style",
    "new_figure",
    "plot_kwargs",
    "style_axes",
]
