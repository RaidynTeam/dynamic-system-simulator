import os
from time import monotonic

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, QEvent, QSettings
from PySide6.QtTest import QTest

from dss.ui.main_window import MainWindow


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def wait_for():
    def wait(predicate, timeout=10):
        deadline = monotonic() + timeout
        while not predicate():
            assert monotonic() < deadline, "Timed out waiting for Qt operation"
            QTest.qWait(5)
    return wait


@pytest.fixture
def window(app, tmp_path, wait_for):
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    widget = MainWindow(settings=settings)
    yield widget
    widget.close()
    wait_for(lambda: widget._job is None)
    widget.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
