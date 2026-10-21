"""End-to-end checks use production solvers, plotting, metrics and export."""

from dataclasses import replace
import gc
from itertools import combinations
import weakref

import numpy as np
import pytest
from matplotlib.colors import to_hex
from PIL import Image
from PySide6.QtCore import QCoreApplication, QEvent, QTimer
from PySide6.QtWidgets import QFileDialog

from dss.ui import controller, presentation
from dss.visualization import compute_error, method_color


METHODS = ("analytical", "euler", "rk4")
SELECTIONS = [combo for n in (1, 2, 3) for combo in combinations(METHODS, n)]
LABELS = {"analytical": "Exact", "euler": "Euler", "rk4": "RK4"}


def run(window, wait_for):
    window.run_button.click()
    wait_for(lambda: window._job is None)
    assert window.status.text() == "Simulation completed. Results loaded."


@pytest.mark.parametrize("case", range(3))
@pytest.mark.parametrize("methods", SELECTIONS)
def test_real_selected_curves_and_metrics(window, wait_for, case, methods):
    window.case_buttons[case].click()
    for name, check in window.method_checks.items():
        check.setChecked(name in methods)
    run(window, wait_for)
    responses = window.last_responses
    assert tuple(r.method for r in responses) == methods
    lines = window.figure.axes[0].lines
    assert [line.get_label() for line in lines] == [LABELS[m] for m in methods]
    for line, response in zip(lines, responses):
        np.testing.assert_array_equal(line.get_xdata(), response.t)
        np.testing.assert_array_equal(line.get_ydata(), response.y)
        np.testing.assert_array_equal(response.t, responses[0].t)
    has_errors = "analytical" in methods and len(methods) > 1
    assert window.view_selector.isEnabled() == has_errors
    if has_errors:
        for response in responses[1:]:
            actual = compute_error(responses[0], response)
            assert window.prepared_results.metrics[response.method] == actual
            assert f"Max |error|: {actual.max_abs:.6g}" in window.metrics.text()
            assert f"RMSE: {actual.rmse:.6g}" in window.metrics.text()
        window.view_selector.setCurrentIndex(1)
        for line, response in zip(window.figure.axes[0].lines, responses[1:]):
            np.testing.assert_array_equal(line.get_ydata(), np.abs(responses[0].y - response.y))
    else:
        assert window.prepared_results.metrics == {}
        assert "Not calculated" in window.metrics.text()


def test_theme_rebuild_preserves_data_metrics_view_and_releases_figures(window, app, wait_for, monkeypatch):
    run(window, wait_for)
    window.view_selector.setCurrentIndex(1)
    responses, metrics = window.last_responses, window.prepared_results.metrics
    def forbidden(*args):
        pytest.fail("Theme/view changes must not execute solvers or metrics")
    monkeypatch.setattr(controller, "run_simulation", forbidden)
    window.prepared_results = replace(window.prepared_results, api=replace(window.prepared_results.api, compute_error=forbidden))
    for mode in ("dark", "light", "dark"):
        old = [weakref.ref(window.figure), weakref.ref(window.canvas)]
        window.set_theme(mode, persist=False)
        assert window.view_selector.currentIndex() == 1
        assert window.last_responses is responses
        assert window.prepared_results.metrics is metrics
        for view in (0, 1):
            window.view_selector.setCurrentIndex(view)
            for line in window.figure.axes[0].lines:
                method = next(m for m in METHODS if LABELS[m] in line.get_label())
                assert to_hex(line.get_color()).lower() == method_color(method, mode).lower()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        app.processEvents()
        gc.collect()
        assert all(ref() is None for ref in old)


@pytest.mark.parametrize("mode", ["light", "dark"])
@pytest.mark.parametrize("view", [0, 1])
@pytest.mark.parametrize("suffix", ["png", "pdf"])
def test_real_export_current_view(window, wait_for, monkeypatch, tmp_path, mode, view, suffix):
    window.set_theme(mode, persist=False)
    run(window, wait_for)
    window.view_selector.setCurrentIndex(view)
    figure = window.figure
    destination = tmp_path / f"{mode}-{view}.{suffix}"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(destination), ""))
    window.export_current(suffix)
    assert window.figure is figure
    assert window.status.text() == f"Exported {destination.name}"
    assert destination.stat().st_size > 1000
    if suffix == "png":
        with Image.open(destination) as image:
            image.verify()
        with Image.open(destination) as image:
            expected = tuple(round(c * 255) for c in figure.get_facecolor()[:3])
            assert image.convert("RGB").getpixel((0, 0)) == expected
    else:
        assert destination.read_bytes().startswith(b"%PDF-")
        assert b"%%EOF" in destination.read_bytes()[-100:]


def test_visualization_failure_preserves_accepted_computation(window, wait_for, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("plot backend unavailable")
    monkeypatch.setattr(presentation, "load_visualization_api", fail)
    window.t_end.setText("1")
    run_inputs = window.input_state()
    window.run_button.click()
    wait_for(lambda: window._job is None)
    assert "Visualization failed: plot backend unavailable" == window.status.text()
    assert len(window.last_responses) == 3
    assert window.last_run_inputs == run_inputs
    assert window.prepared_results is None
    assert not window.export_png.isEnabled()
    assert not window.figure.axes


def test_lab_step_halving_converges_with_real_metrics(window, wait_for):
    initial = window.dt.value()
    errors = []
    for step in range(3):
        assert window.dt.value() == pytest.approx(initial / 2**step)
        run(window, wait_for)
        errors.append(window.prepared_results.metrics)
        window.halve_dt.click()
    for method in ("euler", "rk4"):
        assert errors[2][method].max_abs < errors[1][method].max_abs < errors[0][method].max_abs
        assert errors[2][method].rmse < errors[1][method].rmse < errors[0][method].rmse


def test_large_grid_keeps_worker_responsive_and_preserves_every_sample(window, wait_for):
    window.t_end.setText("10")
    window.dt.setValue(0.0001)
    ticks = []
    timer = QTimer()
    timer.setInterval(5)
    timer.timeout.connect(lambda: ticks.append(window._job is not None))
    timer.start()
    try:
        run(window, wait_for)
    finally:
        timer.stop()
    assert sum(ticks) > 2
    assert len(window.last_responses[0].t) == 100001
    assert all(len(line.get_xdata()) == 100001 for line in window.figure.axes[0].lines)
    window.canvas.draw()


def test_zero_byte_export_cannot_report_success(window, wait_for, monkeypatch, tmp_path):
    run(window, wait_for)
    destination = tmp_path / "empty.png"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(destination), ""))
    window.prepared_results = replace(window.prepared_results, api=replace(
        window.prepared_results.api, export_figure=lambda f, p: p.touch()))
    window.export_current("png")
    assert "Export failed" in window.status.text()


def test_replaced_canvas_cannot_draw_a_detached_figure(window, app, wait_for, monkeypatch, capsys):
    window.show()
    run(window, wait_for)
    old_canvas = window.canvas
    old_canvas.draw_idle()
    assert old_canvas._draw_pending
    window.view_selector.setCurrentIndex(1)
    assert not old_canvas._draw_pending
    app.processEvents()
    assert "Traceback" not in capsys.readouterr().err


def test_failed_theme_rebuild_clears_figures_but_keeps_computation(window, wait_for):
    run(window, wait_for)
    responses = window.last_responses
    def fail(*args, **kwargs):
        raise RuntimeError("theme drawing failed")
    window.prepared_results = replace(window.prepared_results, api=replace(
        window.prepared_results.api, build_response_figure=fail))
    window.set_theme("dark", persist=False)
    assert window.last_responses is responses
    assert window.prepared_results is None
    assert not window.export_pdf.isEnabled()
    assert not window.figure.axes
    assert window.status.text() == "Visualization failed: theme drawing failed"
