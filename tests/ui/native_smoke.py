"""Run explicitly on Windows: python tests/ui/native_smoke.py (not pytest)."""

import os
from pathlib import Path
import sys
import traceback

os.environ["QT_QPA_PLATFORM"] = "windows"

from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from dss.ui.main_window import MainWindow


def main() -> int:
    app = QApplication([])
    window = MainWindow()
    window.show()

    def inspect():
        try:
            assert app.platformName() == "windows"
            assert window.isVisible()
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
            window.case_buttons[0].click()
            window.resize(1440, 900)
            app.processEvents()
            output = Path(".venv")
            assert window.grab().scaled(window.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation).save(str(output / "ui-m25-native-1440x900.png"))
            window.resize(window.minimumSize())
            app.processEvents()
            assert window.run_button.visibleRegion().boundingRect().height() >= 40
            for field in (window.a1, window.a0, window.b0, window.dt):
                assert field.slider.visibleRegion().boundingRect().height() > 0
            assert window.grab().scaled(window.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation).save(str(output / "ui-m25-native-minimum.png"))
            window.close()
            assert not window.isVisible()
            print("PASS: native Windows sliders, presets, Auto dt, halving, invalid input, Run, minimum layout, close.")
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
