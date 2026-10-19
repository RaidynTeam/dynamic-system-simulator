"""Run explicitly on Windows: python tests/ui/native_smoke.py (not pytest)."""

import os
from pathlib import Path
import sys
import traceback

os.environ["QT_QPA_PLATFORM"] = "windows"

from PySide6.QtCore import QSettings, QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from dss.ui.main_window import MainWindow


def main() -> int:
    app = QApplication([])
    settings = QSettings(str(Path(".venv") / "native-smoke.ini"), QSettings.Format.IniFormat)
    settings.clear()
    window = MainWindow(settings=settings)
    window.show()

    def inspect():
        try:
            assert app.platformName() == "windows"
            assert window.isVisible()
            window.theme_toggle.click()
            assert window.theme_mode == "dark"
            window.theme_toggle.click()
            assert window.theme_mode == "light"
            assert not window.export_png.isEnabled()
            assert not window.export_pdf.isEnabled()
            assert not window.view_selector.isEnabled()
            QTest.keyClick(window.a1.slider, Qt.Key.Key_Right)
            assert window.a1.value() == 1.01
            for case in (1, 2, 0):
                window.case_buttons[case].click()
                assert window.a1.value() == case + 1
            window.a0.slider.setValue(400)
            initial = window.dt.value()
            window.halve_dt.click()
            assert window.dt.value() == initial / 2
            assert not window.auto_dt.isChecked()
            window.auto_dt.setChecked(True)
            assert window.dt.value() == initial
            window.method_checks["euler"].click()
            assert "euler" not in window.input_state().methods
            window.method_checks["euler"].click()
            assert "euler" in window.input_state().methods
            window.t_end.setText("invalid")
            assert window.status.text().startswith("Input error:")
            window.t_end.setText("20")
            window.run_button.click()
            assert "No results have been calculated" in window.status.text()
            output = Path(".venv")
            for mode in ("light", "dark"):
                window.set_theme(mode, persist=False)
                window.case_buttons[1].click()
                assert window.a1.value() == 2
                initial = window.dt.value()
                window.halve_dt.click()
                assert window.dt.value() == initial / 2
                window.auto_dt.setChecked(True)
                assert window.dt.value() == initial
                window.case_buttons[0].click()
                for width, height in ((1440, 900), (1000, 740)):
                    window.resize(width, height)
                    app.processEvents()
                    # Native Windows may first constrain a restore after the
                    # minimum-size capture to the monitor work area. Reapply
                    # the requested client size after those window events.
                    window.resize(width, height)
                    app.processEvents()
                    window.canvas.draw()
                    assert window.width() == width and window.height() == height
                    assert window.run_button.visibleRegion().boundingRect().height() >= 40
                    for field in (window.a1, window.a0, window.b0, window.dt):
                        assert field.slider.visibleRegion().boundingRect().height() > 0
                    path = output / f"ui-m3-{mode}-{width}x{height}.png"
                    assert window.grab().scaled(window.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation).save(str(path))
            window.close()
            assert not window.isVisible()
            print("PASS: native Windows Light/Dark, sliders, presets, Auto dt, halving, invalid input, methods, Run, both sizes, close.")
            app.exit(0)
        except Exception:
            traceback.print_exc()
            window.close()
            app.exit(1)

    QTimer.singleShot(300, inspect)
    QTimer.singleShot(10000, lambda: app.exit(2))
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
