"""Isolated UI boundaries; test doubles are never used by production startup."""

import gc
from types import SimpleNamespace
import weakref

import numpy as np
import pytest
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QFileDialog, QMessageBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from dss.contracts import ErrorMetrics, Response
from dss.ui import presentation
from dss.ui.presentation import VisualizationAPI, VisualizationUnavailable, prepare_results


@pytest.fixture
def responses():
    # Clearly isolated TEST DOUBLE samples, not accuracy claims or solver output.
    t = np.array([0.0, 1.0], dtype=np.float64)
    return [Response(t, t, t, name) for name in ("analytical", "euler", "rk4")]


@pytest.fixture
def api():
    def figure(*args, **kwargs):
        result = Figure()
        result.text(0.5, 0.5, "TEST DOUBLE")
        return result

    return VisualizationAPI(figure, figure, lambda *args: ErrorMetrics(1.25, 0.5), lambda fig, path: fig.savefig(path))


def flush(app):
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
    gc.collect()


def test_missing_visualization_is_explicit_and_startup_stays_empty(window, monkeypatch, responses):
    monkeypatch.setattr(presentation, "import_module", lambda name: SimpleNamespace())
    with pytest.raises(VisualizationUnavailable, match="Person 4"):
        presentation.load_visualization_api()
    assert not window.show_responses(responses)
    assert window.prepared_results is None
    assert window.metrics.text() == "No results yet"
    assert not window.export_png.isEnabled()
    assert not window.export_pdf.isEnabled()
    assert not window.view_selector.isEnabled()
    assert "unavailable" in window.status.text()


def test_public_api_loader_uses_exports(monkeypatch, api):
    monkeypatch.setattr(presentation, "import_module", lambda name: api)
    assert presentation.load_visualization_api() == api


def test_matching_results_delegate_figure_and_metric_work(window, responses, api):
    assert window.show_responses(responses, api=api)
    assert window.figure is window.prepared_results.response_figure
    assert window.export_png.isEnabled() and window.export_pdf.isEnabled()
    assert window.view_selector.isEnabled()
    assert "Max |error|: 1.25" in window.metrics.text()
    assert "RMSE: 0.5" in window.metrics.text()
    assert "#FF1D8D" in window.legend_preview.text()
    window.view_selector.setCurrentIndex(1)
    assert window.figure is window.prepared_results.error_figure


def test_without_exact_no_metric_or_error_view_is_fabricated(window, responses, api):
    assert window.show_responses(responses[1:], api=api)
    assert not window.view_selector.isEnabled()
    assert window.prepared_results.metrics == {}
    assert "Not calculated" in window.metrics.text()
    assert window.export_png.isEnabled()


@pytest.mark.parametrize("case", ["empty", "type", "duplicate", "grid", "invalid"])
def test_invalid_responses_rejected_before_visualization(responses, api, case):
    if case == "empty":
        responses = []
    elif case == "type":
        responses = [object()]
    elif case == "duplicate":
        responses = [responses[0], responses[0]]
    elif case == "grid":
        responses[1].t[1] = 0.5
    else:
        responses[1].y[1] = np.nan
    calls = []
    rejected = VisualizationAPI(lambda *args: calls.append(1), api.build_error_figure, api.compute_error, api.export_figure)
    with pytest.raises(ValueError):
        prepare_results(responses, rejected)
    assert not calls


def test_wrong_metrics_and_figures_are_rejected(responses, api):
    wrong_metrics = VisualizationAPI(api.build_response_figure, api.build_error_figure, lambda *args: (0, 0), api.export_figure)
    with pytest.raises(ValueError, match="ErrorMetrics"):
        prepare_results(responses, wrong_metrics)
    wrong_figure = VisualizationAPI(lambda *args, **kwargs: None, api.build_error_figure, api.compute_error, api.export_figure)
    with pytest.raises(ValueError, match="Figure"):
        prepare_results(responses, wrong_figure)


def test_repeated_replacement_releases_old_canvases_and_figures(window, app, responses, api):
    assert window.show_responses(responses, api=api)
    references = []
    for index in range(20):
        references.append(weakref.ref(window.canvas))
        window.view_selector.setCurrentIndex(1 if index % 2 == 0 else 0)
        flush(app)
        assert len(window.plot_card.findChildren(FigureCanvasQTAgg)) == 1
    assert all(reference() is None for reference in references)
    old_figures = [weakref.ref(window.prepared_results.response_figure), weakref.ref(window.prepared_results.error_figure)]
    window.show_responses(responses, api=api)
    flush(app)
    assert all(reference() is None for reference in old_figures)


def test_input_changes_and_failure_clear_previous_results(window, responses, api):
    window.show_responses(responses, api=api)
    window.b0.slider.setValue(200)
    assert window.prepared_results is None
    assert window.metrics.text() == "No results yet"
    assert not window.export_png.isEnabled()
    window.show_responses(responses, api=api)
    assert not window.show_responses([], api=api)
    assert not window.export_pdf.isEnabled()
    assert window.metrics.text() == "No results yet"


def test_theme_and_view_changes_do_not_invalidate_results(window, app, responses, api):
    window.show_responses(responses, api=api)
    prepared = window.prepared_results
    for mode in ("dark", "light", "dark"):
        window.set_theme(mode, persist=False)
        window.view_selector.setCurrentIndex(1)
        window.view_selector.setCurrentIndex(0)
        flush(app)
        assert window.prepared_results.responses == prepared.responses
        assert window.prepared_results.metrics is prepared.metrics
        assert window.export_png.isEnabled()
        assert len(window.plot_card.findChildren(FigureCanvasQTAgg)) == 1


@pytest.mark.parametrize("suffix", ["png", "pdf"])
def test_export_success_delegates_actual_file_write(window, responses, api, monkeypatch, tmp_path, suffix):
    window.show_responses(responses, api=api)
    destination = tmp_path / f"plot.{suffix}"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: (str(destination), ""))
    window.export_current(suffix)
    assert destination.is_file() and destination.stat().st_size > 0
    assert window.status.text() == f"Exported plot.{suffix}"


def test_cancel_and_overwrite_rejection_do_not_export(window, responses, api, monkeypatch, tmp_path):
    window.show_responses(responses, api=api)
    before = window.status.text()
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: ("", ""))
    window.export_current("png")
    assert window.status.text() == before
    destination = tmp_path / "plot.png"
    destination.write_bytes(b"original")
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: (str(destination), ""))
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.No)
    window.export_current("png")
    assert destination.read_bytes() == b"original"
    assert window.status.text() == before
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes)
    window.export_current("png")
    assert destination.read_bytes() != b"original"
    assert window.status.text() == "Exported plot.png"


def test_export_failure_and_wrong_extension_report_error(window, responses, api, monkeypatch, tmp_path):
    def fail(*args):
        raise OSError("disk unavailable")
    failing = VisualizationAPI(api.build_response_figure, api.build_error_figure, api.compute_error, fail)
    window.show_responses(responses, api=failing)
    destination = tmp_path / "plot.png"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: (str(destination), ""))
    window.export_current("png")
    assert "Export failed: disk unavailable" in window.status.text()
    assert not destination.exists()
    window.export_current("pdf")
    assert "Choose a .pdf file" in window.status.text()


def test_missing_results_and_missing_file_cannot_report_success(window, responses, api, monkeypatch, tmp_path):
    window.export_current("png")
    assert "requires simulation results" in window.status.text()
    no_write = VisualizationAPI(api.build_response_figure, api.build_error_figure, api.compute_error, lambda *args: None)
    window.show_responses(responses, api=no_write)
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: (str(tmp_path / "plot"), ""))
    window.export_current("png")
    assert "did not create" in window.status.text()
