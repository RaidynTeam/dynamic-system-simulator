import pytest
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QComboBox, QGroupBox, QTableWidget

from dss.ui.colors import METHOD_COLORS
from dss.ui.theme import apply_light_theme


def test_theme_overrides_dark_palette(app, window):
    dark = QPalette()
    dark.setColor(QPalette.ColorRole.Window, QColor("#101010"))
    dark.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
    app.setPalette(dark)
    apply_light_theme(app)
    assert app.palette().color(QPalette.ColorRole.Window).name() == "#f8fafc"
    assert app.palette().color(QPalette.ColorRole.Base).name() == "#ffffff"
    assert app.palette().color(QPalette.ColorRole.Text).name() == "#0f172a"
    assert app.palette().color(QPalette.ColorRole.Highlight).name() == "#2563eb"
    assert window.figure.get_facecolor() == (1, 1, 1, 1)


@pytest.mark.parametrize("size", [(1440, 900), (1000, 740)])
def test_all_inputs_fit_without_scrolling(window, app, size):
    window.resize(*size)
    window.show()
    app.processEvents()
    bounds = window.centralWidget().rect()
    for widget in (
        *window.case_buttons, window.a1.slider, window.a0.slider, window.b0.slider,
        window.dt.slider, window.auto_dt, window.halve_dt, window.double_dt,
        window.t_end, *window.method_checks.values(), window.run_button,
        window.view_selector, window.export_png, window.export_pdf, window.theme_toggle,
    ):
        assert widget.isVisible()
        assert widget.visibleRegion().boundingRect().size() == widget.size(), widget.objectName()
        origin = widget.mapTo(window.centralWidget(), widget.rect().topLeft())
        assert bounds.contains(origin), widget.objectName()
        assert bounds.contains(origin + widget.rect().bottomRight()), widget.objectName()
    assert window.plot_card.width() > window.control_card.width() * 1.6
    assert window.canvas.height() >= 240
    assert window.status.height() <= 48
    assert window.findChildren(QComboBox) == [window.view_selector]
    assert not window.findChildren(QGroupBox)
    assert not window.findChildren(QTableWidget)


def test_method_colors_and_development_copy(window):
    assert METHOD_COLORS == {"analytical": "#475569", "euler": "#FF1D8D", "rk4": "#2563EB"}
    for method, check in window.method_checks.items():
        assert METHOD_COLORS[method] in check.styleSheet()
    assert window.status.text() == "Ready to simulate"
    assert window.metrics.text() == "No results yet"
    assert window.dt.readout.text() == "0.6283 s"


def test_error_and_visualization_pending_status_are_distinct(window, wait_for):
    window.t_end.setText("invalid")
    assert window.status.property("state") == "error"
    window.t_end.setText("20")
    assert window.status.property("state") == "ready"
    window.run_button.click()
    wait_for(lambda: window._job is None)
    assert window.status.property("state") == "notice"
    assert "Visualization pending" in window.status.text()
