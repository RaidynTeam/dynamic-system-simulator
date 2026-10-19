import gc
from math import pi
import weakref

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QSlider

from dss.ui.main_window import MainWindow


def test_closed_window_is_released_without_signal_reference_cycles(app):
    widget = MainWindow()
    reference = weakref.ref(widget)
    widget.close()
    del widget
    gc.collect()
    app.processEvents()
    assert reference() is None


@pytest.mark.parametrize("name", ["a1", "a0", "b0"])
def test_integer_coefficient_slider_synchronizes_readout_and_state(window, name):
    field = getattr(window, name)
    assert isinstance(field.slider, QSlider)
    field.slider.setValue(237)
    assert field.value() == 2.37
    assert field.readout.text() == "2.37"
    assert getattr(window.input_state(), name) == 2.37
    field.setValue(4.25)
    assert field.slider.value() == 425
    assert field.readout.text() == "4.25"


@pytest.mark.parametrize("name", ["a1", "a0", "b0"])
@pytest.mark.parametrize("position,expected", [(1, 0.01), (2000, 20)])
def test_positive_coefficient_boundaries(window, name, position, expected):
    field = getattr(window, name)
    field.slider.setValue(position)
    assert field.value() == expected
    QTest.keyClick(field.slider, Qt.Key.Key_Right if position == 2000 else Qt.Key.Key_Left)
    assert field.value() == expected


@pytest.mark.parametrize("value", [0, -1, 20.01, float("nan"), float("inf"), 1.005])
def test_rejected_coefficient_value_is_not_silently_clamped(window, value):
    old = window.a1.value()
    assert not window.a1.setValue(value)
    assert window.a1.value() == old
    assert "Input error:" in window.status.text()
    assert "previous value was kept" in window.status.text()


def test_dt_slider_is_logarithmic_with_synchronized_readout(window):
    window.dt.slider.setValue(200)
    assert window.dt.value() == pytest.approx(1e-5)
    window.dt.slider.setValue(400)
    assert window.dt.value() == pytest.approx(1e-4)
    assert window.dt.readout.text() == "0.0001 s"
    assert not window.auto_dt.isChecked()
    assert window.input_state().dt == window.dt.value()


def test_auto_dt_follows_a0_without_quantizing_formula(window):
    assert window.auto_dt.isChecked()
    assert window.dt.value() == 0.2 * pi
    window.a0.slider.setValue(400)
    assert window.dt.value() == 0.1 * pi
    assert window.auto_dt.isChecked()
    assert window.dt.readout.text() == "0.3142 s"
    assert window.dt.value() == 0.1 * pi
    assert "0.314159265358979" in window.dt.readout.toolTip()


def test_manual_override_and_reenable_auto(window):
    window.dt.slider.setValue(800)
    manual = window.dt.value()
    assert not window.auto_dt.isChecked()
    window.a0.slider.setValue(400)
    assert window.dt.value() == manual
    window.auto_dt.setChecked(True)
    assert window.dt.value() == 0.1 * pi
    window.dt.setValue(0.01)
    window._reset_step()
    assert window.auto_dt.isChecked()
    assert window.dt.value() == 0.1 * pi


@pytest.mark.parametrize("index", [0, 1, 2])
def test_preset_updates_sliders_and_restores_auto(window, index):
    window.b0.slider.setValue(250)
    window.a0.slider.setValue(400)
    window.dt.setValue(0.01)
    window.case_buttons[index].click()
    assert window.case_group.checkedId() == index
    assert window.a1.slider.value() == (index + 1) * 100
    assert window.a0.slider.value() == 100
    assert window.b0.slider.value() == 250
    assert window.dt.value() == 0.2 * pi
    assert window.auto_dt.isChecked()


def test_repeated_halving_is_exact_and_doubling_restores_step(window):
    initial = window.dt.value()
    for exponent in range(1, 16):
        window.halve_dt.click()
        assert window.dt.value() == initial / 2**exponent
        assert not window.auto_dt.isChecked()
    for _ in range(15):
        window.double_dt.click()
    assert window.dt.value() == initial


@pytest.mark.parametrize("position,value,button", [(0, 1e-6, "halve_dt"), (1400, 10, "double_dt")])
def test_dt_boundaries_report_rejected_scaling(window, position, value, button):
    window.dt.slider.setValue(position)
    assert window.dt.value() == value
    getattr(window, button).click()
    assert window.dt.value() == value
    assert "previous value was kept" in window.status.text()


@pytest.mark.parametrize("text", ["", "abc", "0", "-1", "nan", "inf", "1,5", "1e308"])
def test_invalid_end_time_has_feedback_and_no_silent_correction(window, text):
    window.t_end.setText(text)
    window.run_button.click()
    assert window.status.text().startswith("Input error:")
    assert window.t_end.text() == text
    assert not window.figure.axes


def test_sample_budget_feedback_and_recovery(window):
    window.dt.setValue(1e-6)
    assert "1,000,000 samples" in window.status.text()
    window.t_end.setText("0.5")
    assert not window.status.text().startswith("Input error:")
    window.t_end.setText("20")
    window.auto_dt.setChecked(True)
    assert not window.status.text().startswith("Input error:")


def test_end_control_and_fixed_api_start_constraint(window):
    assert window.input_state().t0 == 0
    window.t_end.setText("2.5e1")
    assert window.input_state().config_kwargs()["t_end"] == 25
    from dss.ui.state import LabInputs
    with pytest.raises(ValueError, match="Start time must be zero"):
        LabInputs(t0=1).validate()
