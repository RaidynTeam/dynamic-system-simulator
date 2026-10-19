"""The figure factory must stay Qt-free, headless and free of global state."""

import pytest
from matplotlib.figure import Figure

from dss.visualization import (
    DEFAULT_DPI,
    DEFAULT_SIZE,
    apply_figure_theme,
    figure_theme,
    new_figure,
    plot_kwargs,
    style_axes,
)


def rgba(hex_color):
    from matplotlib.colors import to_rgba

    return to_rgba(hex_color)


def test_new_figure_returns_a_bare_matplotlib_figure():
    figure = new_figure()
    assert isinstance(figure, Figure)
    assert figure.axes == []
    assert figure.canvas is not None  # Matplotlib attaches a non-GUI stub
    assert "qt" not in type(figure.canvas).__name__.lower()


def test_new_figure_uses_the_theme_surface_as_its_background():
    for mode in ("light", "dark"):
        figure = new_figure(mode)
        assert figure.get_facecolor() == rgba(figure_theme(mode).surface)


def test_default_geometry_is_applied():
    figure = new_figure()
    assert tuple(figure.get_size_inches()) == DEFAULT_SIZE
    assert figure.dpi == DEFAULT_DPI


def test_every_call_returns_a_distinct_figure():
    first, second = new_figure(), new_figure()
    assert first is not second
    first.add_subplot().plot([0, 1], [0, 1])
    # A repeated run must not keep drawing onto the previous figure.
    assert second.axes == []


@pytest.mark.parametrize("mode", ["", "Dark", "system", None, 3])
def test_invalid_mode_is_rejected(mode):
    with pytest.raises(ValueError):
        new_figure(mode)


@pytest.mark.parametrize("size", [(0, 4.5), (7.2, -1), (True, 4.5)])
def test_invalid_geometry_is_rejected(size):
    with pytest.raises(ValueError):
        new_figure(size=size)


def test_invalid_dpi_is_rejected():
    with pytest.raises(ValueError):
        new_figure(dpi=0)


def test_style_axes_keeps_the_grid_below_the_data_and_drops_two_spines():
    theme = figure_theme("light")
    axes = new_figure().add_subplot()
    style_axes(axes, "light")
    assert axes.get_axisbelow() is True
    for axis in (axes.xaxis, axes.yaxis):
        gridlines = axis.get_gridlines()
        assert gridlines and all(line.get_visible() for line in gridlines)
        assert all(line.get_color() == theme.grid for line in gridlines)
    assert not axes.spines["top"].get_visible()
    assert not axes.spines["right"].get_visible()
    assert axes.spines["left"].get_edgecolor() == rgba(theme.spine)
    assert axes.get_facecolor() == rgba(theme.surface)


def test_style_axes_colors_text_with_text_tokens_not_curve_colors():
    theme = figure_theme("dark")
    axes = new_figure("dark").add_subplot()
    axes.set_title("Step response")
    axes.set_xlabel("Time (s)")
    style_axes(axes, "dark")
    assert axes.title.get_color() == theme.text
    assert axes.xaxis.label.get_color() == theme.secondary


def test_style_axes_themes_an_existing_legend():
    theme = figure_theme("dark")
    axes = new_figure("dark").add_subplot()
    axes.plot([0, 1], [0, 1], **plot_kwargs("euler", "dark"))
    axes.legend()
    style_axes(axes, "dark")
    legend = axes.get_legend()
    assert legend.get_frame().get_facecolor() == rgba(theme.surface)
    assert all(text.get_color() == theme.text for text in legend.get_texts())


def test_apply_figure_theme_switches_an_already_built_figure():
    figure = new_figure("light")
    axes = figure.add_subplot()
    style_axes(axes, "light")
    (line,) = axes.plot([0, 1], [0, 1], **plot_kwargs("euler", "light"))

    assert apply_figure_theme(figure, "dark") is figure
    dark = figure_theme("dark")
    assert figure.get_facecolor() == rgba(dark.surface)
    assert axes.get_facecolor() == rgba(dark.surface)
    # Curve identity is not repainted; only the surroundings change.
    assert line.get_color() == "#FF1D8D"


def test_apply_figure_theme_rejects_non_figures():
    with pytest.raises(ValueError):
        apply_figure_theme(object(), "light")
    with pytest.raises(ValueError):
        apply_figure_theme(new_figure(), "system")


def test_figure_renders_headless_on_an_agg_canvas():
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    figure = new_figure("dark")
    axes = figure.add_subplot()
    axes.plot([0.0, 1.0, 2.0], [0.0, 0.5, 0.9], **plot_kwargs("rk4", "dark"))
    axes.set_title("Headless render")
    axes.legend()
    style_axes(axes, "dark")

    canvas = FigureCanvasAgg(figure)
    canvas.draw()
    assert figure.canvas is canvas
    width, height = canvas.get_width_height()
    assert (width, height) == (DEFAULT_SIZE[0] * DEFAULT_DPI, DEFAULT_SIZE[1] * DEFAULT_DPI)


def test_canvas_can_be_detached_the_way_the_ui_replaces_it():
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    figure = new_figure()
    canvas = FigureCanvasAgg(figure)
    assert figure.canvas is canvas
    figure.set_canvas(None)
    assert figure.canvas is None
