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
                window.case_selector.setCurrentIndex(case)
                assert window.a1.value() == case + 1
            window.a0.slider.setValue(400)
            initial = window.dt.value()
            window.halve_dt.click()
            assert window.dt.value() == initial / 2
            assert not window.auto_dt.isChecked()
            window.auto_dt.setChecked(True)
            assert window.dt.value() == initial
            window.t_end.setText("invalid")
            assert window.status.text().startswith("Input error:")
            window.t_end.setText("20")
            window.run_button.click()
            assert "No results have been calculated" in window.status.text()
            output = Path(".venv")
            assert window.grab().save(str(output / "ui-m2-native.png"))
            window.resize(window.minimumSize())
            app.processEvents()
            assert window.run_button.visibleRegion().boundingRect().height() >= 40
            assert window.grab().save(str(output / "ui-m2-native-minimum.png"))
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
