from math import pi

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QWidget

from dss.ui.controller import M1_STATUS, run_simulation


def test_window_opens_and_closes(window, app):
    window.show()
    app.processEvents()
    assert window.isVisible()
    assert window.close()
    app.processEvents()
    assert not window.isVisible()


def test_required_controls_and_empty_results(window):
    for name in (
        "a1", "a0", "b0", "t_end", "dt", "case_1", "case_2", "case_3",
        "method_analytical", "method_euler", "method_rk4", "run_simulation",
        "plot_placeholder", "error_metrics", "simulation_status",
    ):
        assert window.findChild(QWidget, name) is not None, name
    assert "CMPE 443" in window.windowTitle()
    assert all(check.isChecked() for check in window.method_checks.values())
    assert not window.figure.axes
    assert window.metrics.text() == "No results yet"


@pytest.mark.parametrize("index,a1", [(0, 1), (1, 2), (2, 3)])
def test_case_presets_and_contract_mapping(window, index, a1):
    window.b0.setValue(2.5)
    window.case_buttons[index].click()
    state = window.input_state()
    assert state.model_kwargs() == dict(a2=1, a1=a1, a0=1, u0=2.5, y0=0, v0=0)
    assert state.config_kwargs() == dict(t0=0, t_end=20, dt=state.dt)
    assert state.dt == pytest.approx(0.2 * pi, abs=1e-8)


def test_initial_step_custom_parameters_and_refinement(window):
    window.a0.setValue(4)
    assert window.case_group.checkedId() == -1
    assert window.dt.value() == pytest.approx(0.1 * pi, abs=1e-8)
    window.dt.setValue(0.01)
    assert window.input_state().dt == 0.01
    window._reset_step()
    assert window.dt.value() == pytest.approx(0.1 * pi, abs=1e-8)


def test_run_reports_m1_unavailability_and_selection_error(window, app):
    window.show()
    app.processEvents()
    QTest.mouseClick(window.run_button, Qt.MouseButton.LeftButton)
    assert window.status.text() == M1_STATUS
    for check in window.method_checks.values():
        check.setChecked(False)
    QTest.mouseClick(window.run_button, Qt.MouseButton.LeftButton)
    assert window.status.text() == "Input error: Select at least one method."
    window.method_checks["rk4"].setChecked(True)
    QTest.mouseClick(window.run_button, Qt.MouseButton.LeftButton)
    assert window.input_state().methods == ("rk4",)
    assert window.status.text() == M1_STATUS
    assert not window.figure.axes


def test_minimum_window_contains_plot_and_status(window, app):
    window.resize(window.minimumSize())
    window.show()
    app.processEvents()
    assert window.canvas.width() >= 300
    assert window.canvas.height() >= 200
    assert window.status.visibleRegion().boundingRect().height() >= 26
    assert window.run_button.visibleRegion().boundingRect().height() >= 40


def test_controller_rejects_missing_shared_inputs():
    with pytest.raises(ValueError, match="ModelParams"):
        run_simulation(None, None, ("analytical",))
