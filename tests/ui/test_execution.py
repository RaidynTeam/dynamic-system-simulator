"""Real Run calculation and controlled scheduling tests, without fake plots."""

from dataclasses import FrozenInstanceError
import gc
from threading import Event
import weakref

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QThread, QTimer
from PySide6.QtTest import QSignalSpy

from dss.contracts import ModelParams, Response, SimulationConfig
from dss.ui import controller
from dss.ui.execution import SimulationThread


@pytest.fixture
def held_solver(monkeypatch):
    """Pause scheduling only; the real controller still produces all responses."""
    entered, release = Event(), Event()
    calls = []
    original = controller.run_simulation

    def run(model, config, methods):
        calls.append((model, config, methods, QThread.currentThread()))
        entered.set()
        if not release.wait(10):
            raise TimeoutError("Test did not release the controlled worker")
        return original(model, config, methods)

    monkeypatch.setattr(controller, "run_simulation", run)
    yield entered, release, calls
    release.set()  # Always allow teardown to drain the worker, even on assertion failure.


def drain(app):
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
    gc.collect()


@pytest.mark.parametrize("case", [0, 1, 2])
@pytest.mark.parametrize("methods", [("analytical",), ("euler",), ("rk4",), ("analytical", "euler", "rk4")])
def test_run_button_real_cases_and_selections(window, wait_for, case, methods):
    window.case_buttons[case].click()
    window.t_end.setText("2")
    window.dt.setValue(0.05)
    for name, check in window.method_checks.items():
        check.setChecked(name in methods)
    window.run_button.click()
    assert not window.run_button.isEnabled()
    assert window.status.text() == "Calculating..."
    wait_for(lambda: window._job is None)
    assert window.run_button.isEnabled()
    assert tuple(r.method for r in window.last_responses) == methods
    assert all(isinstance(r, Response) for r in window.last_responses)
    assert window.last_run_inputs.a1 == case + 1
    assert window.status.text() == "Calculation completed. Visualization pending."
    assert not window.figure.axes
    assert window.metrics.text() == "No results yet"
    assert not window.export_png.isEnabled() and not window.export_pdf.isEnabled()


def test_immutable_snapshot_and_shared_parameter_transfer(window, app, wait_for, held_solver, monkeypatch):
    entered, release, calls = held_solver
    window.a1.setValue(2.5)
    window.a0.setValue(4)
    window.b0.setValue(3)
    window.dt.setValue(0.025)
    window.t_end.setText("1.375")
    expected = window.input_state()
    snapshots = []
    original_input = window.input_state
    def capture_once():
        value = original_input()
        snapshots.append(value)
        return value
    monkeypatch.setattr(window, "input_state", capture_once)
    window.run_button.click()
    wait_for(entered.is_set)
    request = window._job.request
    assert len(snapshots) == 1 and request.inputs is snapshots[0]
    assert request.inputs == expected
    with pytest.raises(FrozenInstanceError):
        request.revision = 999
    model, config, methods, thread = calls[0]
    assert isinstance(model, ModelParams) and isinstance(config, SimulationConfig)
    assert (model.a1, model.a0, model.b0) == (2.5, 4, 3)
    assert (config.t0, config.t_end, config.dt) == (0, 1.375, 0.025)
    assert methods == expected.methods
    assert thread is not app.thread()
    release.set()
    wait_for(lambda: window._job is None)
    assert window.last_run_inputs == expected


def test_gui_heartbeat_and_repeated_run_clicks(window, app, wait_for, held_solver, monkeypatch):
    entered, release, calls = held_solver
    updates = []
    original_status = window._set_status

    def check_thread(*args):
        updates.append(QThread.currentThread() == app.thread())
        original_status(*args)

    monkeypatch.setattr(window, "_set_status", check_thread)
    window.run_button.click()
    wait_for(entered.is_set)
    heartbeat = []
    timer = QTimer()
    timer.timeout.connect(lambda: heartbeat.append(1))
    timer.start(5)
    try:
        for _ in range(10):
            window.run_button.click()
            window._run_requested()  # A queued/shortcut invocation is guarded too.
        window.theme_toggle.click()
        assert window.theme_mode == "dark"
        wait_for(lambda: len(heartbeat) >= 3)
        assert len(calls) == 1
        assert window.status.text() == "Calculating..."
    finally:
        timer.stop()
        release.set()
    wait_for(lambda: window._job is None)
    assert window.last_responses is not None
    assert all(updates), "A worker touched a UI status widget"
    assert window.theme_mode == "dark"


def test_gui_heartbeat_during_real_rk4_calculation(window, wait_for):
    window.t_end.setText("10")
    window.dt.setValue(0.001)
    for name, check in window.method_checks.items():
        check.setChecked(name == "rk4")
    ticks = []
    timer = QTimer()
    timer.timeout.connect(lambda: ticks.append(window._job is not None))
    timer.start(5)
    try:
        window.run_button.click()
        wait_for(lambda: window._job is None)
        assert any(ticks), "GUI timer did not run while actual RK4 was active"
        assert window.last_responses[0].method == "rk4"
    finally:
        timer.stop()
        timer.timeout.disconnect()


@pytest.mark.parametrize("change", ["a1", "end", "invalid_end", "method", "case", "dt", "change_back"])
def test_changed_inputs_reject_stale_responses(window, wait_for, held_solver, change):
    entered, release, calls = held_solver
    window.run_button.click()
    wait_for(entered.is_set)
    original_snapshot = window._job.request.inputs
    if change in ("a1", "change_back"):
        window.a1.setValue(1.5)
        if change == "change_back":
            window.a1.setValue(1)
    elif change in ("end", "invalid_end"):
        window.t_end.setText("10" if change == "end" else "invalid")
    elif change == "method":
        window.method_checks["rk4"].setChecked(False)
    elif change == "case":
        window.case_buttons[1].click()
    else:
        window.halve_dt.click()
    assert window._job.request.inputs == original_snapshot
    assert window.status.text().startswith("Calculating...")
    release.set()
    wait_for(lambda: window._job is None)
    assert window.last_responses is None and window.last_run_inputs is None
    assert "results discarded" in window.status.text()
    assert window.metrics.text() == "No results yet"
    assert not window.export_png.isEnabled()


@pytest.mark.parametrize("method", ["euler", "rk4"])
def test_real_solver_overflow_is_shown_without_results(window, wait_for, method):
    window.a1.setValue(20)
    window.a0.setValue(20)
    window.dt.setValue(10)
    window.t_end.setText("10000")
    for name, check in window.method_checks.items():
        check.setChecked(name == method)
    window.run_button.click()
    wait_for(lambda: window._job is None)
    assert "calculation overflowed" in window.status.text()
    assert window.status.property("state") == "error"
    assert window.last_responses is None
    assert window.run_button.isEnabled()


def test_worker_preserves_original_exception_object(window, wait_for, monkeypatch):
    error = FloatingPointError("Original controller error")
    def fail(*args):
        raise error
    monkeypatch.setattr(controller, "run_simulation", fail)
    window.run_button.click()
    spy = QSignalSpy(window._job.outcome_ready)
    wait_for(lambda: window._job is None)
    assert spy.count() == 1
    assert spy.at(0)[0].error is error
    assert window.status.text() == "Calculation failed: Original controller error"


def test_repeated_runs_replace_results_and_release_workers(window, app, wait_for):
    previous = []
    window.t_end.setText("1")
    for _ in range(5):
        window.run_button.click()
        wait_for(lambda: window._job is None)
        drain(app)
        assert not window.findChildren(SimulationThread)
        assert all(reference() is None for reference in previous)
        previous = [weakref.ref(response) for response in window.last_responses]
    window.b0.setValue(2)
    drain(app)
    assert window.last_responses is None
    assert all(reference() is None for reference in previous)


def test_safe_close_defers_until_worker_finishes(window, app, wait_for, held_solver):
    entered, release, calls = held_solver
    window.show()
    window.run_button.click()
    wait_for(entered.is_set)
    assert not window.close()
    assert window.isVisible() and window._closing
    assert "Finishing calculation before closing" in window.status.text()
    assert "cancel" not in window.status.text().lower()
    release.set()
    wait_for(lambda: window._job is None and not window.isVisible())
    drain(app)
    assert not window.findChildren(SimulationThread)
    assert window.last_responses is None


def test_no_run_for_invalid_input_and_recovery(window, wait_for):
    window.t_end.setText("invalid")
    window.run_button.click()
    assert window._job is None
    assert window.status.text().startswith("Input error:")
    window.t_end.setText("1")
    window.run_button.click()
    wait_for(lambda: window._job is None)
    assert window.last_responses is not None
