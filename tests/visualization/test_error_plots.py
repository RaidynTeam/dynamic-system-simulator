"""The error figure must plot the measured difference, not a redrawn response."""

import numpy as np
import pytest

from dss.analytical import solve_analytical
from dss.contracts import ModelParams, Response, SimulationConfig
from dss.numerical import make_time_grid, solve_euler, solve_rk4
from dss.visualization import (
    DEFAULT_ERROR_TITLE_TEMPLATE,
    ERROR_LABEL_TEMPLATE,
    MAX_MARKERS,
    TIME_LABEL,
    build_error_figure,
    build_response_figure,
    error_signal,
    figure_theme,
    method_color,
)


def make_response(method, y=None, t=None):
    t = np.linspace(0.0, 4.0, 9, dtype=np.float64) if t is None else t
    y = np.linspace(0.0, 1.0, t.size, dtype=np.float64) if y is None else y
    return Response(t=t, y=y, v=np.zeros_like(t), method=method)


def real_set(a1=1.0, dt=0.2, t_end=6.0):
    model = ModelParams(a1=a1, a0=1.0, b0=1.0)
    t = make_time_grid(SimulationConfig(t0=0.0, t_end=t_end, dt=dt))
    exact = solve_analytical(model, t)
    return exact, [solve_euler(model, t), solve_rk4(model, t)]


def lines_by_label(figure):
    return {line.get_label(): line for line in figure.axes[0].get_lines()}


# --- what is drawn -----------------------------------------------------------


def test_each_candidate_gets_one_curve_and_the_reference_gets_none():
    exact, candidates = real_set()
    figure = build_error_figure(exact, candidates)
    assert set(lines_by_label(figure)) == {"Euler", "RK4"}


def test_one_candidate_draws_one_curve():
    exact, candidates = real_set()
    figure = build_error_figure(exact, [candidates[0]])
    assert list(lines_by_label(figure)) == ["Euler"]


def test_the_curve_is_the_absolute_difference_not_the_response():
    exact, candidates = real_set()
    figure = build_error_figure(exact, candidates)
    lines = lines_by_label(figure)
    for candidate, label in zip(candidates, ("Euler", "RK4")):
        expected = error_signal(exact, candidate)
        assert np.array_equal(lines[label].get_ydata(), expected)
        assert np.array_equal(lines[label].get_xdata(), exact.t)
        # The response itself must not be what got drawn.
        assert not np.array_equal(lines[label].get_ydata(), candidate.y)


def test_every_plotted_value_is_nonnegative():
    exact, candidates = real_set()
    figure = build_error_figure(exact, candidates)
    for line in figure.axes[0].get_lines():
        assert np.all(line.get_ydata() >= 0.0)


def test_the_first_sample_has_zero_error_because_every_solver_starts_there():
    exact, candidates = real_set()
    figure = build_error_figure(exact, candidates)
    for line in figure.axes[0].get_lines():
        assert line.get_ydata()[0] == 0.0


def test_an_exact_match_draws_a_flat_zero_line():
    reference = make_response("analytical")
    identical = make_response("euler", y=reference.y.copy())
    figure = build_error_figure(reference, [identical])
    (line,) = figure.axes[0].get_lines()
    assert np.all(line.get_ydata() == 0.0)


def test_the_curves_keep_their_method_identities():
    exact, candidates = real_set()
    figure = build_error_figure(exact, candidates)
    lines = lines_by_label(figure)
    assert lines["Euler"].get_color() == method_color("euler", "light")
    assert lines["RK4"].get_color() == method_color("rk4", "light")


def test_legend_order_is_stable_whatever_order_the_caller_used():
    exact, candidates = real_set()
    forward = build_error_figure(exact, candidates)
    backward = build_error_figure(exact, list(reversed(candidates)))
    labels = lambda f: [t.get_text() for t in f.axes[0].get_legend().get_texts()]
    assert labels(forward) == labels(backward) == ["Euler", "RK4"]


def test_the_figure_depends_on_the_data_it_was_given():
    exact, candidates = real_set(dt=0.4)
    fine_exact, fine_candidates = real_set(dt=0.1)
    coarse = build_error_figure(exact, candidates)
    fine = build_error_figure(fine_exact, fine_candidates)
    coarse_peak = lines_by_label(coarse)["Euler"].get_ydata().max()
    fine_peak = lines_by_label(fine)["Euler"].get_ydata().max()
    assert fine_peak < coarse_peak


# --- labelling ---------------------------------------------------------------


def test_title_axis_labels_legend_and_grid_are_present():
    exact, candidates = real_set()
    axes = build_error_figure(exact, candidates).axes[0]
    assert axes.get_title() == DEFAULT_ERROR_TITLE_TEMPLATE.format(reference="Exact")
    assert axes.get_xlabel() == TIME_LABEL
    assert axes.get_ylabel() == ERROR_LABEL_TEMPLATE.format(reference="Exact")
    assert axes.get_legend() is not None
    assert all(line.get_visible() for line in axes.yaxis.get_gridlines())


def test_the_labels_name_the_reference_that_was_actually_used():
    reference = make_response("rk4")
    candidate = make_response("euler")
    axes = build_error_figure(reference, [candidate]).axes[0]
    assert "RK4" in axes.get_ylabel()
    assert "RK4" in axes.get_title()


def test_the_error_label_states_no_physical_unit():
    label = ERROR_LABEL_TEMPLATE.format(reference="Exact")
    for forbidden in ("V", "volt", "m", "metre", "meter", "rad", "A"):
        assert f"({forbidden})" not in label


def test_a_caller_supplied_title_replaces_the_default():
    exact, candidates = real_set()
    figure = build_error_figure(exact, candidates, title="Case 1 error, dt=0.2 s")
    assert figure.axes[0].get_title() == "Case 1 error, dt=0.2 s"


@pytest.mark.parametrize("title", ["", "   ", 5, b"x"])
def test_an_unusable_title_is_rejected(title):
    exact, candidates = real_set()
    with pytest.raises(ValueError):
        build_error_figure(exact, candidates, title=title)


# --- the axis scale ----------------------------------------------------------


def test_the_default_axis_is_linear():
    exact, candidates = real_set()
    assert build_error_figure(exact, candidates).axes[0].get_yscale() == "linear"


def test_a_log_axis_can_be_requested():
    exact, candidates = real_set()
    assert build_error_figure(exact, candidates, scale="log").axes[0].get_yscale() == "log"


def test_a_log_axis_masks_the_zero_samples_without_replacing_them():
    # A log axis cannot place a zero, so those samples are masked out. Nothing
    # invents a floor value: the real zero stays in the underlying data.
    exact, candidates = real_set()
    figure = build_error_figure(exact, candidates, scale="log")
    for line in figure.axes[0].get_lines():
        drawn = line.get_ydata()
        assert np.ma.isMaskedArray(drawn)
        assert drawn.mask[0]
        assert drawn.data[0] == 0.0
        assert np.all(drawn.compressed() > 0.0)


def test_a_linear_axis_draws_the_zero_samples_unmasked():
    exact, candidates = real_set()
    figure = build_error_figure(exact, candidates)
    for line in figure.axes[0].get_lines():
        drawn = line.get_ydata()
        assert not np.ma.isMaskedArray(drawn)
        assert drawn[0] == 0.0


def test_a_log_figure_still_renders_with_zero_samples_present():
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    exact, candidates = real_set()
    figure = build_error_figure(exact, candidates, scale="log")
    FigureCanvasAgg(figure).draw()


@pytest.mark.parametrize("scale", ["", "symlog", "logarithmic", None, 2])
def test_an_unknown_scale_is_rejected(scale):
    exact, candidates = real_set()
    with pytest.raises(ValueError):
        build_error_figure(exact, candidates, scale=scale)


# --- themes ------------------------------------------------------------------


def test_the_contract_positional_call_still_works():
    exact, candidates = real_set()
    figure = build_error_figure(exact, candidates)
    assert len(figure.axes[0].get_lines()) == 2


def test_dark_theme_uses_the_dark_surface_and_curve_colours():
    from matplotlib.colors import to_rgba

    exact, candidates = real_set()
    figure = build_error_figure(exact, candidates, theme="dark")
    assert figure.get_facecolor() == to_rgba(figure_theme("dark").surface)
    assert lines_by_label(figure)["RK4"].get_color() == method_color("rk4", "dark")


@pytest.mark.parametrize("theme", ["", "Dark", "system", None])
def test_an_unknown_theme_is_rejected(theme):
    exact, candidates = real_set()
    with pytest.raises(ValueError):
        build_error_figure(exact, candidates, theme=theme)


# --- rejected input ----------------------------------------------------------


@pytest.mark.parametrize("empty", [[], ()])
def test_an_empty_candidate_list_is_rejected(empty):
    exact, _ = real_set()
    with pytest.raises(ValueError):
        build_error_figure(exact, empty)


@pytest.mark.parametrize("bad", [None, "euler", 3, [None], ["euler"], [object()]])
def test_candidates_that_are_not_responses_are_rejected(bad):
    exact, _ = real_set()
    with pytest.raises(ValueError):
        build_error_figure(exact, bad)


@pytest.mark.parametrize("bad", [None, "analytical", 3, []])
def test_a_reference_that_is_not_a_response_is_rejected(bad):
    _, candidates = real_set()
    with pytest.raises(ValueError):
        build_error_figure(bad, candidates)


def test_a_single_candidate_outside_a_list_is_rejected():
    exact, candidates = real_set()
    with pytest.raises(ValueError):
        build_error_figure(exact, candidates[0])


def test_the_same_candidate_method_twice_is_rejected():
    exact, candidates = real_set()
    with pytest.raises(ValueError):
        build_error_figure(exact, [candidates[0], candidates[0]])


def test_a_candidate_sharing_the_reference_method_is_rejected():
    exact, candidates = real_set()
    with pytest.raises(ValueError):
        build_error_figure(exact, [exact])


def test_a_candidate_on_a_different_grid_is_rejected():
    exact, _ = real_set(dt=0.2)
    _, other = real_set(dt=0.1)
    with pytest.raises(ValueError, match="time grid"):
        build_error_figure(exact, [other[0]])


def test_a_corrupted_candidate_is_caught_by_the_shared_validator():
    exact, candidates = real_set()
    object.__setattr__(candidates[0], "y", np.full(candidates[0].y.size, np.inf))
    with pytest.raises(ValueError):
        build_error_figure(exact, candidates)


# --- the function keeps its hands off the caller's data ----------------------


def test_the_call_does_not_modify_the_supplied_arrays():
    exact, candidates = real_set()
    before = [(r.t.copy(), r.y.copy(), r.v.copy()) for r in [exact, *candidates]]
    build_error_figure(exact, candidates, theme="dark", scale="log")
    for result, (t, y, v) in zip([exact, *candidates], before):
        assert np.array_equal(result.t, t)
        assert np.array_equal(result.y, y)
        assert np.array_equal(result.v, v)


def test_the_call_does_not_reorder_the_callers_list():
    exact, candidates = real_set()
    original = list(candidates)
    build_error_figure(exact, candidates)
    assert candidates == original


def test_consecutive_calls_never_draw_onto_the_previous_figure():
    exact, candidates = real_set()
    first = build_error_figure(exact, candidates)
    second = build_error_figure(exact, [candidates[0]])
    assert first is not second
    assert len(first.axes[0].get_lines()) == 2
    assert len(second.axes[0].get_lines()) == 1


def test_the_response_and_error_views_are_separate_figure_objects():
    # dss.ui.presentation refuses to display them if they are the same object.
    exact, candidates = real_set()
    response_figure = build_response_figure([exact, *candidates])
    error_figure = build_error_figure(exact, candidates)
    assert response_figure is not error_figure
    assert len(response_figure.axes[0].get_lines()) == 3
    assert len(error_figure.axes[0].get_lines()) == 2


# --- dense grids and headless rendering --------------------------------------


def test_markers_are_thinned_so_a_dense_grid_stays_readable():
    exact, candidates = real_set(dt=0.002, t_end=20.0)
    assert exact.t.size > 1000
    figure = build_error_figure(exact, candidates)
    line = lines_by_label(figure)["Euler"]
    drawn = len(range(0, exact.t.size, line.get_markevery()))
    assert drawn <= MAX_MARKERS + 1


def test_the_figure_renders_headless_on_an_agg_canvas():
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    exact, candidates = real_set()
    figure = build_error_figure(exact, candidates, theme="dark")
    canvas = FigureCanvasAgg(figure)
    canvas.draw()
    assert figure.canvas is canvas
