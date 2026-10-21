"""The response figure must show the real data, and nothing it was not given."""

import numpy as np
import pytest

from dss.analytical import solve_analytical
from dss.contracts import ModelParams, Response, SimulationConfig
from dss.numerical import make_time_grid, solve_euler, solve_rk4
from dss.visualization import (
    DEFAULT_RESPONSE_TITLE,
    MAX_MARKERS,
    METHOD_LABELS,
    OUTPUT_LABEL,
    TIME_LABEL,
    build_response_figure,
    figure_theme,
    method_color,
)

CASES = {1: 1.0, 2: 2.0, 3: 3.0}  # a1 per handout case, with a0 = b0 = 1.


def make_response(method, t=None, y=None):
    t = np.linspace(0.0, 4.0, 9, dtype=np.float64) if t is None else t
    y = np.linspace(0.0, 1.0, t.size, dtype=np.float64) if y is None else y
    return Response(t=t, y=y, v=np.zeros_like(t), method=method)


def real_responses(a1=1.0, dt=0.2, t_end=6.0):
    model = ModelParams(a1=a1, a0=1.0, b0=1.0)
    t = make_time_grid(SimulationConfig(t0=0.0, t_end=t_end, dt=dt))
    return [solve_analytical(model, t), solve_euler(model, t), solve_rk4(model, t)]


def lines_by_label(figure):
    return {line.get_label(): line for line in figure.axes[0].get_lines()}


def legend_labels(figure):
    return [text.get_text() for text in figure.axes[0].get_legend().get_texts()]


# --- the data actually drawn -------------------------------------------------


def test_one_method_draws_exactly_one_curve():
    figure = build_response_figure([make_response("euler")])
    assert len(figure.axes) == 1
    assert len(figure.axes[0].get_lines()) == 1
    assert list(lines_by_label(figure)) == ["Euler"]


def test_three_methods_draw_three_curves_with_their_own_identities():
    figure = build_response_figure(real_responses())
    lines = lines_by_label(figure)
    assert set(lines) == {"Exact", "Euler", "RK4"}
    for method, label in METHOD_LABELS.items():
        assert lines[label].get_color() == method_color(method, "light")


def test_curves_carry_the_supplied_samples_unchanged():
    responses = real_responses()
    figure = build_response_figure(responses)
    lines = lines_by_label(figure)
    for response in responses:
        line = lines[METHOD_LABELS[response.method]]
        assert np.array_equal(line.get_xdata(), response.t)
        assert np.array_equal(line.get_ydata(), response.y)


def test_velocity_is_not_plotted():
    # M2 compares y(t) only; v belongs to no curve in this figure.
    response = make_response("rk4")
    figure = build_response_figure([response])
    (line,) = figure.axes[0].get_lines()
    assert np.array_equal(line.get_ydata(), response.y)


@pytest.mark.parametrize("case, a1", sorted(CASES.items()))
def test_every_handout_case_draws_all_three_methods(case, a1):
    figure = build_response_figure(real_responses(a1=a1))
    assert set(lines_by_label(figure)) == {"Exact", "Euler", "RK4"}


def test_legend_order_is_stable_whatever_order_the_user_selected():
    responses = real_responses()
    forward = build_response_figure(responses)
    backward = build_response_figure(list(reversed(responses)))
    assert legend_labels(forward) == ["Exact", "Euler", "RK4"]
    assert legend_labels(backward) == ["Exact", "Euler", "RK4"]


# --- labelling ---------------------------------------------------------------


def test_title_axis_labels_legend_and_grid_are_present():
    figure = build_response_figure(real_responses())
    axes = figure.axes[0]
    assert axes.get_title() == DEFAULT_RESPONSE_TITLE
    assert axes.get_xlabel() == TIME_LABEL
    assert axes.get_ylabel() == OUTPUT_LABEL
    assert axes.get_legend() is not None
    assert all(line.get_visible() for line in axes.yaxis.get_gridlines())


def test_output_label_states_no_physical_unit():
    # The handout never says what y measures; an invented unit would be a lie.
    for forbidden in ("V", "volt", "m", "metre", "meter", "rad", "A"):
        assert f"({forbidden})" not in OUTPUT_LABEL
    assert OUTPUT_LABEL == "Output y(t)"


def test_a_caller_supplied_title_replaces_the_default():
    figure = build_response_figure(real_responses(), title="Case 1  a1=1  a0=1  b0=1")
    assert figure.axes[0].get_title() == "Case 1  a1=1  a0=1  b0=1"


@pytest.mark.parametrize("title", ["", "   ", 5, b"x"])
def test_an_unusable_title_is_rejected(title):
    with pytest.raises(ValueError):
        build_response_figure(real_responses(), title=title)


def test_time_axis_starts_at_the_first_sample():
    responses = real_responses(t_end=6.0)
    figure = build_response_figure(responses)
    assert figure.axes[0].get_xlim() == (responses[0].t[0], responses[0].t[-1])


# --- themes ------------------------------------------------------------------


def test_the_contract_positional_call_still_works():
    figure = build_response_figure(real_responses())
    assert len(figure.axes[0].get_lines()) == 3


def test_dark_theme_uses_the_dark_surface_and_curve_colours():
    from matplotlib.colors import to_rgba

    figure = build_response_figure(real_responses(), theme="dark")
    assert figure.get_facecolor() == to_rgba(figure_theme("dark").surface)
    assert lines_by_label(figure)["RK4"].get_color() == method_color("rk4", "dark")


@pytest.mark.parametrize("theme", ["", "Dark", "system", None])
def test_an_unknown_theme_is_rejected(theme):
    with pytest.raises(ValueError):
        build_response_figure(real_responses(), theme=theme)


# --- rejected input ----------------------------------------------------------


@pytest.mark.parametrize("empty", [[], ()])
def test_an_empty_selection_is_rejected(empty):
    with pytest.raises(ValueError):
        build_response_figure(empty)


@pytest.mark.parametrize(
    "bad",
    [None, "euler", 3, {"euler": 1}, [None], ["euler"], [object()]],
)
def test_anything_that_is_not_a_response_list_is_rejected(bad):
    with pytest.raises(ValueError):
        build_response_figure(bad)


def test_a_single_response_outside_a_list_is_rejected():
    with pytest.raises(ValueError):
        build_response_figure(make_response("euler"))


def test_the_same_method_twice_is_rejected():
    with pytest.raises(ValueError):
        build_response_figure([make_response("euler"), make_response("euler")])


def test_different_time_grids_are_rejected_instead_of_interpolated():
    coarse = make_response("euler", t=np.linspace(0.0, 4.0, 9, dtype=np.float64))
    fine = make_response("rk4", t=np.linspace(0.0, 4.0, 17, dtype=np.float64))
    with pytest.raises(ValueError, match="time grid"):
        build_response_figure([coarse, fine])


def test_same_length_but_different_samples_are_rejected():
    first = make_response("euler", t=np.linspace(0.0, 4.0, 9, dtype=np.float64))
    second = make_response("rk4", t=np.linspace(0.0, 8.0, 9, dtype=np.float64))
    with pytest.raises(ValueError, match="time grid"):
        build_response_figure([first, second])


def test_a_corrupted_response_is_caught_by_the_shared_validator():
    response = make_response("euler")
    object.__setattr__(response, "y", np.array([np.nan, 1.0], dtype=np.float64))
    with pytest.raises(ValueError):
        build_response_figure([response])


# --- the function keeps its hands off the caller's data ----------------------


def test_the_call_does_not_modify_the_supplied_arrays():
    responses = real_responses()
    before = [(r.t.copy(), r.y.copy(), r.v.copy()) for r in responses]
    build_response_figure(responses, theme="dark")
    for response, (t, y, v) in zip(responses, before):
        assert np.array_equal(response.t, t)
        assert np.array_equal(response.y, y)
        assert np.array_equal(response.v, v)


def test_the_call_does_not_reorder_the_callers_list():
    responses = real_responses()
    original = list(responses)
    build_response_figure(responses)
    assert responses == original


def test_consecutive_calls_never_draw_onto_the_previous_figure():
    responses = real_responses()
    first = build_response_figure(responses)
    second = build_response_figure([responses[0]])
    assert first is not second
    assert len(first.axes[0].get_lines()) == 3
    assert len(second.axes[0].get_lines()) == 1


# --- dense grids -------------------------------------------------------------


def test_markers_are_thinned_so_a_dense_grid_stays_readable():
    dense = real_responses(dt=0.002, t_end=20.0)
    assert dense[0].t.size > 1000
    figure = build_response_figure(dense)
    euler = lines_by_label(figure)["Euler"]
    drawn = len(range(0, dense[0].t.size, euler.get_markevery()))
    assert drawn <= MAX_MARKERS + 1


def test_a_short_grid_keeps_every_marker():
    figure = build_response_figure([make_response("euler")])
    (line,) = figure.axes[0].get_lines()
    assert line.get_markevery() == 1


def test_the_reference_curve_draws_no_markers():
    figure = build_response_figure(real_responses())
    assert lines_by_label(figure)["Exact"].get_marker() == "None"


# --- headless ----------------------------------------------------------------


def test_the_figure_renders_headless_on_an_agg_canvas():
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    figure = build_response_figure(real_responses(), theme="dark")
    canvas = FigureCanvasAgg(figure)
    canvas.draw()
    assert figure.canvas is canvas
