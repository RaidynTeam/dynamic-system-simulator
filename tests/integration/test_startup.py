"""Exercise the real entry point in an isolated interpreter and Qt event loop."""

import os
from pathlib import Path
import subprocess
import sys
import textwrap


def test_entry_point_without_unfinished_modules():
    script = textwrap.dedent('''
        import importlib.abc
        import runpy
        import sys
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication

        class BlockUnfinished(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                prefixes = ("dss.contracts", "dss.analytical", "dss.numerical",
                            "dss.visualization", "dss.demo_data")
                if any(fullname == p or fullname.startswith(p + ".") for p in prefixes):
                    raise AssertionError("Startup imported unfinished module: " + fullname)
                return None

        sys.meta_path.insert(0, BlockUnfinished())
        original_exec = QApplication.exec
        def timed_exec(app):
            def inspect_and_close():
                windows = [w for w in app.topLevelWidgets() if w.isVisible()]
                if len(windows) != 1:
                    app.exit(2)
                    return
                # Opening the UI must remain isolated. Run now intentionally
                # needs shared types and real solvers (covered separately).
                if windows[0].status.text() != "Ready to simulate":
                    app.exit(3)
                    return
                windows[0].close()
            inspection = QTimer()
            inspection.setSingleShot(True)
            inspection.timeout.connect(inspect_and_close)
            watchdog = QTimer()
            watchdog.setSingleShot(True)
            watchdog.timeout.connect(lambda: app.exit(4))
            inspection.start(100)
            watchdog.start(5000)
            try:
                return original_exec()
            finally:
                inspection.stop()
                watchdog.stop()
                inspection.timeout.disconnect()
                watchdog.timeout.disconnect()
        QApplication.exec = timed_exec
        runpy.run_module("dss", run_name="__main__")
    ''')
    result = subprocess.run(
        [sys.executable, "-X", "faulthandler", "-c", script],
        cwd=Path(__file__).resolve().parents[2],
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
        capture_output=True, text=True, timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
