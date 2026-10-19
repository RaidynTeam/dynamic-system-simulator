import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from dss.ui.main_window import MainWindow


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def window(app):
    widget = MainWindow()
    yield widget
    widget.close()
    widget.deleteLater()
    app.processEvents()
