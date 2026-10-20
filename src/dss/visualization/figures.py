"""Qt-free, pyplot-free Figure construction for the Lab 1 comparison views.

`matplotlib.figure.Figure` is imported directly and `matplotlib.pyplot` is never
imported, so no figure is registered in a global manager, nothing has to be
closed to avoid a leak, and no backend is selected on import. Person 3 attaches
the returned figure to a `FigureCanvasQTAgg`; export attaches an Agg canvas.
Every call returns a new figure, so repeated runs cannot draw onto an old one.
"""

from matplotlib.figure import Figure

from .styles import Mode, figure_theme

#: Fits the 65% results column at the supported 1000x740 window without scrolling.
DEFAULT_SIZE: tuple[float, float] = (7.2, 4.5)
DEFAULT_DPI: int = 100


def new_figure(
    mode: Mode = "light",
    *,
    size: tuple[float, float] = DEFAULT_SIZE,
    dpi: int = DEFAULT_DPI,
) -> Figure:
    """Create an empty themed figure with no axes and no canvas attached.

    Constrained layout matches the UI's own placeholder figure and keeps titles
    and legends inside the canvas when Qt resizes it.
    """
    theme = figure_theme(mode)
    width, height = size
    for name, value in (("width", width), ("height", height), ("dpi", dpi)):
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"{name} must be a positive number")
    figure = Figure(figsize=(width, height), dpi=dpi, layout="constrained")
    figure.set_facecolor(theme.surface)
    figure.set_edgecolor(theme.surface)
    return figure


def style_axes(axes, mode: Mode = "light") -> None:
    """Apply the project's recessive axes style to one Axes in place.

    Top and right spines are removed and the grid is drawn beneath the data, so
    the curves stay the most prominent marks in the figure.
    """
    theme = figure_theme(mode)
    axes.set_facecolor(theme.surface)
    axes.set_axisbelow(True)
    axes.grid(True, which="major", color=theme.grid, linewidth=0.8, alpha=1.0)
    for side in ("top", "right"):
        axes.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        axes.spines[side].set_visible(True)
        axes.spines[side].set_color(theme.spine)
        axes.spines[side].set_linewidth(1.0)
    axes.tick_params(colors=theme.secondary, labelcolor=theme.secondary, width=1.0)
    axes.title.set_color(theme.text)
    axes.xaxis.label.set_color(theme.secondary)
    axes.yaxis.label.set_color(theme.secondary)
    _style_legend(axes, theme)


def _style_legend(axes, theme) -> None:
    legend = axes.get_legend()
    if legend is None:
        return
    frame = legend.get_frame()
    frame.set_facecolor(theme.surface)
    frame.set_edgecolor(theme.spine)
    frame.set_alpha(1.0)
    for text in legend.get_texts():
        text.set_color(theme.text)
    title = legend.get_title()
    if title is not None:
        title.set_color(theme.text)


def apply_figure_theme(figure: Figure, mode: Mode = "light") -> Figure:
    """Re-theme an existing figure so the UI can switch theme without replotting.

    Curve colors are not repainted here: a line drawn with one theme's identity
    keeps it, because repainting would need to know which method each line is.
    Rebuild the figure to change curve colors.
    """
    if not isinstance(figure, Figure):
        raise ValueError("figure must be a matplotlib Figure")
    theme = figure_theme(mode)
    figure.set_facecolor(theme.surface)
    figure.set_edgecolor(theme.surface)
    suptitle = figure.get_suptitle()
    if suptitle:
        figure.suptitle(suptitle, color=theme.text)
    for axes in figure.axes:
        style_axes(axes, mode)
    return figure
