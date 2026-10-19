import subprocess
import sys

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor, QPalette

from dss.ui.theme import THEMES, saved_theme


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_switch_themes_preserves_layout_and_controls(window, app, mode):
    window.show()
    app.processEvents()
    before = window.control_card.geometry(), window.plot_card.geometry()
    window.set_theme(mode)
    app.processEvents()
    assert before == (window.control_card.geometry(), window.plot_card.geometry())
    theme = THEMES[mode]
    assert app.palette().color(QPalette.ColorRole.Window).name() == theme.background.lower()
    assert QColor.fromRgbF(*window.figure.get_facecolor()).name() == theme.card.lower()
    assert window.figure.texts[0].get_color() == theme.secondary
    assert window.canvas.palette().color(QPalette.ColorRole.Window).name() == theme.card.lower()
    window.case_buttons[1].click()
    window.a0.slider.setValue(400)
    initial = window.dt.value()
    window.halve_dt.click()
    assert window.dt.value() == initial / 2
    assert not window.auto_dt.isChecked()
    window.method_checks["euler"].click()
    assert "euler" not in window.input_state().methods
    assert "#FF1D8D" in window.method_checks["euler"].styleSheet()


def test_toggle_persists_across_new_process(window):
    window.theme_toggle.click()
    assert window.theme_mode == "dark"
    path = window.settings.fileName()
    script = "from PySide6.QtCore import QSettings; from dss.ui.theme import saved_theme; import sys; print(saved_theme(QSettings(sys.argv[1], QSettings.Format.IniFormat)))"
    result = subprocess.run([sys.executable, "-c", script, path], text=True, capture_output=True, timeout=15)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "dark"
    from dss.ui.main_window import MainWindow
    relaunched = MainWindow(settings=QSettings(path, QSettings.Format.IniFormat))
    assert relaunched.theme_mode == "dark"
    relaunched.close()
    relaunched.deleteLater()


def test_invalid_saved_setting_falls_back_to_light(window):
    window.settings.setValue("ui/theme", "system")
    assert saved_theme(window.settings) == "light"


def test_dark_mode_ignores_system_light_palette(window, app):
    app.setPalette(QPalette(QColor("white")))
    window.set_theme("dark")
    assert app.palette().color(QPalette.ColorRole.Text).name() == "#f8fafc"
    assert "QToolTip" in app.styleSheet()
    assert "QSlider::handle:horizontal:focus" in app.styleSheet()
