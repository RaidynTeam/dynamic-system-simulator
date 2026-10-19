"""Launch the M1 desktop skeleton with ``python -m dss``."""

import sys

from PySide6.QtWidgets import QApplication

from dss.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Dynamic System Simulator")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
