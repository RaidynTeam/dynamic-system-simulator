"""Opt-in native acceptance of the production UI inside the frozen executable.

No solver replacements: click Run, await its QThread, check actual samples,
figures and metrics, and select export destinations for the production exporter.
"""
import json
import os
from pathlib import Path
import sys
import traceback
from time import monotonic


def main(output_dir: str) -> int:
    os.environ["QT_QPA_PLATFORM"] = "windows"
    from PySide6.QtCore import QSettings, QTimer
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QFileDialog
    import numpy as np
    from PIL import Image
    from dss.ui.main_window import MainWindow

    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = {"passed": False, "frozen": bool(getattr(sys, "frozen", False)),
              "executable": sys.executable, "cases": []}
    app = QApplication([])
    settings = QSettings(str(output / "acceptance.ini"), QSettings.Format.IniFormat)
    settings.clear()
    window = MainWindow(settings=settings)
    window.resize(1440, 900)
    window.show()

    def run():
        window.run_button.click()
        deadline = monotonic() + 60
        while window._job is not None:
            assert monotonic() < deadline, "Worker timeout"
            QTest.qWait(10)
        assert "Results loaded" in window.status.text(), window.status.text()
        assert window.last_responses is not None
        responses = {r.method: r for r in window.last_responses}
        assert set(responses) == {"analytical", "euler", "rk4"}
        assert len(window.figure.axes[0].lines) == 3
        for line, response in zip(window.figure.axes[0].lines, window.last_responses):
            np.testing.assert_array_equal(line.get_ydata(), response.y)
        measured = {}
        for method in ("euler", "rk4"):
            error = np.abs(responses[method].y - responses["analytical"].y)
            expected = (float(error.max()), float(np.sqrt(np.mean(error ** 2))))
            metric = window.prepared_results.metrics[method]
            np.testing.assert_allclose([metric.max_abs, metric.rmse], expected, rtol=1e-12)
            assert f"Max |error|: {metric.max_abs:.6g}" in window.metrics.text()
            assert f"RMSE: {metric.rmse:.6g}" in window.metrics.text()
            measured[method] = {"max_abs": metric.max_abs, "rmse": metric.rmse}
        return responses, measured

    def inspect():
        try:
            assert app.platformName() == "windows"
            assert window.isVisible() and window.windowHandle().isExposed()
            report["window_initialized"] = True
            for check in window.method_checks.values():
                check.setChecked(True)
            for index in range(3):
                window.case_buttons[index].click()
                window.auto_dt.setChecked(True)
                assert (window.a1.value(), window.a0.value(), window.b0.value()) == (index + 1, 1, 1)
                np.testing.assert_allclose(window.dt.value(), 0.2 * np.pi, rtol=1e-5)
                original_dt = window.dt.value()
                window.set_theme("light", persist=False)
                responses, metrics = run()
                auto_metrics = metrics
                # Repeat Run must produce new result objects on the same grid.
                repeated, _ = run()
                assert repeated["euler"] is not responses["euler"]
                np.testing.assert_array_equal(repeated["euler"].y, responses["euler"].y)
                for view in (0, 1):
                    window.view_selector.setCurrentIndex(view)
                    app.processEvents()
                    window.canvas.draw()
                    assert len(window.figure.axes[0].lines) == (3 if view == 0 else 2)
                    if view == 1:
                        for line, method in zip(window.figure.axes[0].lines, ("euler", "rk4")):
                            np.testing.assert_allclose(line.get_ydata(), np.abs(
                                repeated[method].y - repeated["analytical"].y))
                    assert window.grab().save(str(output / f"case-{index + 1}-{'response' if view == 0 else 'error'}.png"))
                window.halve_dt.click()
                assert window.dt.value() == original_dt / 2
                assert not window.auto_dt.isChecked()
                assert window.last_responses is None and not window.export_png.isEnabled()
                window.set_theme("dark", persist=False)
                _, half_metrics = run()
                for method in ("euler", "rk4"):
                    assert half_metrics[method]["max_abs"] < auto_metrics[method]["max_abs"]
                window.theme_toggle.click()
                assert window.theme_mode == "light"
                window.theme_toggle.click()
                assert window.theme_mode == "dark"
                for view in (0, 1):
                    window.view_selector.setCurrentIndex(view)
                    app.processEvents()
                    for suffix in ("png", "pdf"):
                        destination = output / f"export-case-{index + 1}-{view}.{suffix}"
                        original_dialog = QFileDialog.getSaveFileName
                        try:
                            QFileDialog.getSaveFileName = lambda *a, **k: (str(destination), "")
                            window.export_current(suffix)
                        finally:
                            QFileDialog.getSaveFileName = original_dialog
                        assert window.status.text() == f"Exported {destination.name}", window.status.text()
                        assert destination.stat().st_size > 1000
                        if suffix == "png":
                            with Image.open(destination) as im:
                                im.verify()
                        else:
                            assert destination.read_bytes().startswith(b"%PDF-")
                report["cases"].append({"case": index + 1, "auto_dt": original_dt,
                                        "auto_metrics": auto_metrics, "half_metrics": half_metrics})
            assert window.close()
            app.processEvents()
            assert not window.isVisible()
            report["normal_close"] = True
            report["passed"] = True
            app.exit(0)
        except Exception:
            report["last_status"] = window.status.text()
            report["error"] = traceback.format_exc()
            window.close()
            app.exit(1)
        finally:
            (output / "acceptance.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    QTimer.singleShot(500, inspect)
    return app.exec()
