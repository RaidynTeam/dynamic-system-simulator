"""Method identity and figure themes: the agreed values, and no color-only cues."""

import dataclasses
from typing import get_args

import pytest

from dss.contracts import Method
from dss.visualization import styles

AGREED_LIGHT = {"analytical": "#475569", "euler": "#FF1D8D", "rk4": "#2563EB"}


def test_method_order_matches_the_shared_method_names():
    # Drift here would silently leave one solver unstyled or styled twice.
    assert set(styles.METHOD_ORDER) == set(get_args(Method))
    assert len(styles.METHOD_ORDER) == len(get_args(Method))


def test_light_colors_are_the_values_the_team_agreed():
    for method, expected in AGREED_LIGHT.items():
        assert styles.method_color(method, "light") == expected
        assert styles.method_style(method, "light").color == expected


def test_euler_keeps_its_identity_in_dark_mode():
    assert styles.method_color("euler", "dark") == "#FF1D8D"


def test_dark_mode_lightens_only_the_two_low_contrast_curves():
    # Exact 1.93:1 and RK4 2.83:1 on the dark card are below the 3:1 floor.
    for method in ("analytical", "rk4"):
        assert styles.method_color(method, "dark") != AGREED_LIGHT[method]


def test_legend_labels_use_exact_not_the_internal_method_name():
    assert styles.METHOD_LABELS["analytical"] == "Exact"
    assert styles.method_style("analytical").label == "Exact"
    assert "analytical" not in styles.METHOD_LABELS.values()


def test_methods_differ_by_line_style_as_well_as_color():
    linestyles = [styles.method_style(m).linestyle for m in styles.METHOD_ORDER]
    assert len(set(map(str, linestyles))) == len(styles.METHOD_ORDER)


def test_each_mode_defines_every_method():
    for mode in styles.MODES:
        assert set(styles.METHOD_COLORS[mode]) == set(styles.METHOD_ORDER)
        assert styles.figure_theme(mode).mode == mode


def test_reference_curve_is_drawn_thickest_and_below_the_numerical_curves():
    exact = styles.method_style("analytical")
    for method in ("euler", "rk4"):
        candidate = styles.method_style(method)
        assert exact.linewidth > candidate.linewidth
        assert exact.zorder < candidate.zorder


def test_styles_and_themes_are_frozen():
    style = styles.method_style("rk4")
    with pytest.raises(dataclasses.FrozenInstanceError):
        style.color = "#000000"
    with pytest.raises(dataclasses.FrozenInstanceError):
        styles.figure_theme("light").surface = "#000000"


@pytest.mark.parametrize("method", ["", "exact", "Euler", "analytic", None, 1])
def test_unknown_method_is_rejected(method):
    with pytest.raises(ValueError):
        styles.method_style(method)
    with pytest.raises(ValueError):
        styles.method_color(method, "light")


@pytest.mark.parametrize("mode", ["", "Light", "system", "auto", None, 0])
def test_unknown_mode_is_rejected(mode):
    with pytest.raises(ValueError):
        styles.figure_theme(mode)
    with pytest.raises(ValueError):
        styles.method_style("euler", mode)


def test_plot_kwargs_carries_the_label_color_and_style():
    kwargs = styles.plot_kwargs("euler", "dark")
    assert kwargs["label"] == "Euler"
    assert kwargs["color"] == "#FF1D8D"
    assert kwargs["linestyle"] == styles.METHOD_LINESTYLES["euler"]
    assert "markevery" not in kwargs  # the stride depends on the sample count


def test_plot_kwargs_omits_marker_keys_for_the_reference_curve():
    kwargs = styles.plot_kwargs("analytical")
    assert "marker" not in kwargs and "markersize" not in kwargs


def test_plot_kwargs_is_accepted_by_matplotlib():
    from dss.visualization import new_figure

    axes = new_figure().add_subplot()
    for method in styles.METHOD_ORDER:
        (line,) = axes.plot([0.0, 1.0], [0.0, 1.0], **styles.plot_kwargs(method))
        assert line.get_label() == styles.METHOD_LABELS[method]
        assert line.get_color() == styles.method_color(method)
