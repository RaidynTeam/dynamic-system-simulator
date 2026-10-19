"""Compact light-theme desktop presentation; calculation remains deferred."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QVBoxLayout, QWidget,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from dss.ui.colors import METHOD_COLORS
from dss.ui.controller import M1_STATUS
from dss.ui.slider_input import SliderInput
from dss.ui.state import LabInputs
from dss.ui.theme import apply_theme, method_style, saved_theme, theme_settings


class MainWindow(QMainWindow):
    def __init__(self, *, settings=None) -> None:
        super().__init__()
        self.settings = settings if settings is not None else theme_settings()
        self.theme_mode = saved_theme(self.settings)
        self.theme = apply_theme(QApplication.instance(), self.theme_mode)
        self.setWindowTitle("Dynamic System Simulator — CMPE 443 Lab 1")
        self.setMinimumSize(1000, 740)
        self.resize(1440, 900)
        page = QWidget(objectName="page")
        self.setCentralWidget(page)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(18)
        header = QVBoxLayout()
        header.setSpacing(4)
        header.addWidget(QLabel("Dynamic System Simulator", objectName="title"))
        subtitle = QLabel("CMPE 443 · Lab 1 · Unit-Step Response")
        subtitle.setProperty("role", "secondary")
        header.addWidget(subtitle)
        header_row = QHBoxLayout()
        header_row.addLayout(header, 1)
        self.theme_toggle = QPushButton(objectName="theme_toggle")
        self.theme_toggle.setFixedSize(36, 36)
        self.theme_toggle.clicked.connect(self._toggle_theme)
        header_row.addWidget(self.theme_toggle, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header_row)

        body = QHBoxLayout()
        body.setSpacing(24)
        layout.addLayout(body, 1)
        self.control_card = QFrame(objectName="control_card")
        self.control_card.setMaximumHeight(680)
        left = QVBoxLayout(self.control_card)
        left.setContentsMargins(18, 18, 18, 18)
        left.setSpacing(10)
        body.addWidget(self.control_card, 35, Qt.AlignmentFlag.AlignTop)
        left.addWidget(self._section("System Controls"))

        case_row = QHBoxLayout()
        case_row.setSpacing(6)
        self.case_group = QButtonGroup(self)
        self.case_buttons = []
        for index in range(3):
            button = QPushButton(f"Case {index + 1}", objectName=f"case_{index + 1}")
            button.setProperty("case", True)
            button.setCheckable(True)
            button.setMinimumHeight(32)
            button.setToolTip(f"a₁ = {index + 1}, a₀ = 1; preserve b₀ and restore Auto dt.")
            self.case_group.addButton(button, index)
            self.case_buttons.append(button)
            case_row.addWidget(button)
        self.case_buttons[0].setChecked(True)
        self.case_group.idClicked.connect(self._apply_case)
        left.addLayout(case_row)

        self.a1 = SliderInput("a1", 1.0, caption="a₁ · Damping")
        self.a0 = SliderInput("a0", 1.0, caption="a₀ · Restoring")
        self.b0 = SliderInput("b0", 1.0, caption="b₀ · Input gain")
        self.dt = SliderInput("dt", LabInputs.initial_step(1.0), logarithmic=True, caption="dt · Time step")
        for field in (self.a1, self.a0, self.b0, self.dt):
            left.addWidget(field)

        auto_row = QHBoxLayout()
        self.auto_dt = QCheckBox("Auto dt", objectName="auto_dt")
        self.auto_dt.setToolTip("dt = 0.1 × 2π / √a₀; re-enable to restore the lab initial step.")
        self.auto_dt.setChecked(True)
        auto_row.addWidget(self.auto_dt)
        auto_row.addStretch()
        self.halve_dt = QPushButton("dt / 2", objectName="halve_dt")
        self.double_dt = QPushButton("dt × 2", objectName="double_dt")
        for button in (self.halve_dt, self.double_dt):
            button.setProperty("role", "step")
            auto_row.addWidget(button)
        self.halve_dt.clicked.connect(self._halve_step)
        self.double_dt.clicked.connect(self._double_step)
        left.addLayout(auto_row)
        line = QFrame(objectName="divider")
        line.setFixedHeight(1)
        left.addWidget(line)

        time_row = QHBoxLayout()
        time_row.addWidget(QLabel("End time"))
        time_row.addStretch()
        self.t_end = QLineEdit("20", objectName="t_end")
        self.t_end.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.t_end.setMaximumWidth(100)
        self.t_end.setToolTip("End time in seconds. Start time is fixed at 0 s by the lab model (API v0.2).")
        time_row.addWidget(self.t_end)
        time_row.addWidget(QLabel("s"))
        left.addLayout(time_row)

        methods = QHBoxLayout()
        self.method_checks = {}
        for key, label in (("analytical", "Exact"), ("euler", "Euler"), ("rk4", "RK4")):
            check = QCheckBox(label, objectName=f"method_{key}")
            check.setStyleSheet(method_style(key, self.theme_mode))
            check.setChecked(True)
            self.method_checks[key] = check
            methods.addWidget(check)
        methods.addStretch()
        left.addLayout(methods)
        left.addStretch(1)
        self.run_button = QPushButton("Run Simulation", objectName="run_simulation")
        self.run_button.setMinimumHeight(42)
        self.run_button.clicked.connect(self._run_requested)
        left.addWidget(self.run_button)

        results = QVBoxLayout()
        results.setSpacing(12)
        body.addLayout(results, 65)
        results.addWidget(self._section("System Response"))
        self.plot_card = QFrame(objectName="plot_card")
        plot_layout = QVBoxLayout(self.plot_card)
        plot_layout.setContentsMargins(8, 8, 8, 8)
        self.figure = Figure(facecolor=self.theme.card, layout="constrained")
        self.figure.text(0.5, 0.5, "Simulation results will appear here", ha="center", va="center", fontsize=10, color=self.theme.secondary)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setObjectName("plot_placeholder")
        self.canvas.setMinimumSize(300, 240)
        plot_layout.addWidget(self.canvas)
        results.addWidget(self.plot_card, 1)
        results.addSpacing(6)
        results.addWidget(self._section("Error Metrics"))
        self.metrics = QLabel("No results yet", objectName="error_metrics")
        self.metrics.setProperty("role", "secondary")
        results.addWidget(self.metrics)

        footer = QHBoxLayout()
        footer.setSpacing(8)
        self.status_indicator = QLabel("✓", objectName="status_indicator")
        footer.addWidget(self.status_indicator)
        self.status = QLabel("Ready to simulate", objectName="simulation_status")
        self.status.setWordWrap(True)
        self.status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.status.setMinimumHeight(26)
        footer.addWidget(self.status, 1)
        layout.addLayout(footer)

        self.a1.valueChanged.connect(self._mark_custom)
        self.a0.valueChanged.connect(self._a0_changed)
        self.dt.valueChanged.connect(self._manual_step)
        self.auto_dt.toggled.connect(self._auto_changed)
        for field in (self.a1, self.a0, self.b0, self.dt):
            field.valueRejected.connect(self._show_error)
            field.valueChanged.connect(self._refresh_feedback)
        self.t_end.textChanged.connect(self._refresh_feedback)
        for check in self.method_checks.values():
            check.toggled.connect(self._refresh_feedback)
        self._update_theme_widgets()

    def _toggle_theme(self) -> None:
        self.set_theme("dark" if self.theme_mode == "light" else "light")

    def set_theme(self, mode: str, *, persist: bool = True) -> None:
        self.theme = apply_theme(QApplication.instance(), mode)
        self.theme_mode = mode
        if persist:
            self.settings.setValue("ui/theme", mode)
            self.settings.sync()
        self._update_theme_widgets()

    def _update_theme_widgets(self) -> None:
        target = "Dark" if self.theme_mode == "light" else "Light"
        self.theme_toggle.setText("☾" if self.theme_mode == "light" else "☀")
        self.theme_toggle.setToolTip(f"Switch to {target} Mode")
        self.theme_toggle.setAccessibleName(f"Switch to {target} Mode")
        for method, check in self.method_checks.items():
            check.setStyleSheet(method_style(method, self.theme_mode))
        self.figure.set_facecolor(self.theme.card)
        for text in self.figure.texts:
            text.set_color(self.theme.secondary)
        self.canvas.draw_idle()

    @staticmethod
    def _section(text: str) -> QLabel:
        label = QLabel(text)
        label.setProperty("role", "section")
        return label

    def _mark_custom(self) -> None:
        self.case_group.setExclusive(False)
        for button in self.case_buttons:
            button.setChecked(False)
        self.case_group.setExclusive(True)

    def _a0_changed(self) -> None:
        self._mark_custom()
        if self.auto_dt.isChecked():
            self._set_auto_step()

    def _set_auto_step(self) -> None:
        blocked = self.dt.blockSignals(True)
        self.dt.setValue(LabInputs.initial_step(self.a0.value()))
        self.dt.blockSignals(blocked)

    def _auto_changed(self, checked: bool) -> None:
        if checked:
            self._set_auto_step()
        self._refresh_feedback()

    def _manual_step(self) -> None:
        self.auto_dt.setChecked(False)

    def _scale_step(self, factor: float) -> None:
        self.dt.setValue(self.dt.value() * factor)

    def _halve_step(self) -> None:
        self._scale_step(0.5)

    def _double_step(self) -> None:
        self._scale_step(2.0)

    def _reset_step(self) -> None:
        self.auto_dt.setChecked(True)
        self._set_auto_step()
        self._refresh_feedback()

    def _apply_case(self, index: int) -> None:
        for field, value in ((self.a1, float(index + 1)), (self.a0, 1.0)):
            field.blockSignals(True)
            field.setValue(value)
            field.blockSignals(False)
        self._reset_step()

    def input_state(self) -> LabInputs:
        try:
            if "," in self.t_end.text():
                raise ValueError
            t_end = float(self.t_end.text())
        except ValueError:
            raise ValueError("Enter a numeric end time using a decimal point (for example 20.5).") from None
        return LabInputs(
            a1=self.a1.value(), a0=self.a0.value(), b0=self.b0.value(),
            t0=0.0, t_end=t_end, dt=self.dt.value(),
            methods=tuple(key for key, check in self.method_checks.items() if check.isChecked()),
        )

    def _set_status(self, message: str, state: str = "ready") -> None:
        self.status.setText(message)
        self.status_indicator.setText({"ready": "✓", "error": "!", "notice": "i"}[state])
        for widget in (self.status, self.status_indicator):
            widget.setProperty("state", state)
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def _show_error(self, message: str) -> None:
        self._set_status(f"Input error: {message}", "error")

    def _refresh_feedback(self) -> bool:
        try:
            self.input_state().validate()
        except ValueError as error:
            self._show_error(str(error))
            return False
        self._set_status("Ready to simulate")
        return True

    def _run_requested(self) -> None:
        if self._refresh_feedback():
            self._set_status(M1_STATUS, "notice")
