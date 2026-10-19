"""Launch the desktop UI with ``python -m dss``."""

import sys

from PySide6.QtWidgets import QApplication

from dss.ui.main_window import MainWindow
from dss.ui.theme import apply_light_theme


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Dynamic System Simulator")
    apply_light_theme(app)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
