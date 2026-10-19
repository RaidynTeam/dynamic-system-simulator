"""PySide6 presentation layer for the instructor's lab model."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFormLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow, QPushButton,
    QScrollArea, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from dss.ui.controller import M1_STATUS
from dss.ui.colors import METHOD_COLORS
from dss.ui.state import LabInputs
from dss.ui.slider_input import SliderInput


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Dynamic System Simulator — CMPE 443 Lab 1")
        self.setMinimumSize(940, 700)
        self.resize(1120, 800)
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)
        title = QLabel("Dynamic System Simulator")
        font = title.font()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        layout.addWidget(QLabel("CMPE 443 · Lab 1    |    M2 — Slider controls"))
        equation = QLabel("y″ + a₁y′ + a₀y = b₀u(t)    ·    Unit-step input    ·    y(0) = y′(0) = 0")
        equation.setWordWrap(True)
        layout.addWidget(equation)

        body = QHBoxLayout()
        body.setSpacing(20)
        layout.addLayout(body, 1)
        controls = QWidget()
        left = QVBoxLayout(controls)
        left.setContentsMargins(0, 0, 8, 0)
        left.setSpacing(12)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setMinimumWidth(340)
        scroll.setWidget(controls)
        left_column = QVBoxLayout()
        left_column.setSpacing(12)
        left_column.addWidget(scroll, 1)
        body.addLayout(left_column, 2)

        cases = QGroupBox("Lab case")
        case_layout = QVBoxLayout(cases)
        self.case_selector = QComboBox(objectName="case_selector")
        self.case_selector.addItems([
            "Case 1 — Underdamped", "Case 2 — Critically damped",
            "Case 3 — Overdamped", "Custom lab parameters",
        ])
        case_layout.addWidget(self.case_selector)
        case_note = QLabel("Cases set a₁ = 1, 2, 3 and a₀ = 1. b₀ stays editable.")
        case_note.setWordWrap(True)
        case_layout.addWidget(case_note)
        left.addWidget(cases)

        model = QGroupBox("System parameters")
        form = QFormLayout(model)
        self.a1 = SliderInput("a1", 1.0)
        self.a0 = SliderInput("a0", 1.0)
        self.b0 = SliderInput("b0", 1.0)
        for label, field in (("a₁ · damping", self.a1), ("a₀ · restoring", self.a0), ("b₀ · input gain", self.b0)):
            form.addRow(label, field)
        ranges = QLabel("Coefficient range: 0.01–20.00 · step 0.01")
        ranges.setWordWrap(True)
        form.addRow(ranges)
        fixed = QLabel("Lab: a₂ = 1; y₀ = v₀ = t₀ = 0\nLegacy general API: u₀ = b₀")
        fixed.setWordWrap(True)
        form.addRow(fixed)
        left.addWidget(model)

        simulation = QGroupBox("Simulation configuration")
        config = QFormLayout(simulation)
        self.t0 = QLineEdit("0", objectName="t0")
        self.t0.setReadOnly(True)
        self.t0.setToolTip("Fixed at zero by the instructor's lab model and shared API v0.2.")
        self.t_end = QLineEdit("20", objectName="t_end")
        self.t_end.setToolTip("UI default: 20 seconds; choose the desired observation interval.")
        self.dt = SliderInput("dt", LabInputs.initial_step(1.0), logarithmic=True)
        config.addRow("Start time (s)", self.t0)
        config.addRow("End time (s)", self.t_end)
        config.addRow("Time step Δt (s)", self.dt)
        self.auto_dt = QCheckBox("Auto dt · follow a₀", objectName="auto_dt")
        self.auto_dt.setChecked(True)
        config.addRow(self.auto_dt)
        step_actions = QHBoxLayout()
        self.halve_dt = QPushButton("dt / 2", objectName="halve_dt")
        self.double_dt = QPushButton("dt × 2", objectName="double_dt")
        self.halve_dt.clicked.connect(self._halve_step)
        self.double_dt.clicked.connect(self._double_step)
        step_actions.addWidget(self.halve_dt)
        step_actions.addWidget(self.double_dt)
        config.addRow(step_actions)
        reset = QPushButton("Reset Δt to lab initial value", objectName="reset_dt")
        reset.clicked.connect(self._reset_step)
        config.addRow(reset)
        note = QLabel("Initial Δt = 0.1 × 2π / √a₀.\nΔt range: 1 µs–10 s (logarithmic).\nManual Δt changes turn Auto dt off.")
        note.setWordWrap(True)
        config.addRow(note)
        left.addWidget(simulation)

        methods = QGroupBox("Methods")
        method_layout = QHBoxLayout(methods)
        self.method_checks = {}
        for key, label in (("analytical", "Exact"), ("euler", "Euler"), ("rk4", "RK4")):
            check = QCheckBox(label, objectName=f"method_{key}")
            color = METHOD_COLORS[key]
            check.setStyleSheet(
                f"QCheckBox {{ color: {color}; }} "
                f"QCheckBox::indicator:checked {{ background-color: {color}; }}"
            )
            check.setChecked(True)
            self.method_checks[key] = check
            method_layout.addWidget(check)
        left.addWidget(methods)
        self.run_button = QPushButton("Run Simulation", objectName="run_simulation")
        self.run_button.setMinimumHeight(40)
        self.run_button.clicked.connect(self._run_requested)
        left_column.addWidget(self.run_button)
        left.addStretch()

        right = QVBoxLayout()
        right.setSpacing(12)
        body.addLayout(right, 3)
        plot = QGroupBox("System response")
        plot_layout = QVBoxLayout(plot)
        self.figure = Figure(layout="constrained")
        self.figure.text(
            0.5, 0.5, "Plot placeholder\nNo simulation results — UI skeleton",
            ha="center", va="center", fontsize=12, color="#516174",
        )
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setObjectName("plot_placeholder")
        self.canvas.setMinimumSize(300, 200)
        plot_layout.addWidget(self.canvas)
        right.addWidget(plot, 1)

        metrics = QGroupBox("Error metrics · relative to Exact")
        metrics_layout = QVBoxLayout(metrics)
        self.metrics = QTableWidget(2, 3, objectName="error_metrics")
        self.metrics.setHorizontalHeaderLabels(["Method", "Max absolute error", "RMSE"])
        self.metrics.verticalHeader().hide()
        self.metrics.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.metrics.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for row, name in enumerate(("Euler", "RK4")):
            for col, value in enumerate((name, "Not calculated", "Not calculated")):
                self.metrics.setItem(row, col, QTableWidgetItem(value))
            key = ("euler", "rk4")[row]
            self.metrics.item(row, 0).setForeground(QColor(METHOD_COLORS[key]))
        self.metrics.setMaximumHeight(125)
        metrics_layout.addWidget(self.metrics)
        right.addWidget(metrics)

        status_group = QGroupBox("Simulation status")
        status_layout = QVBoxLayout(status_group)
        self.status = QLabel(M1_STATUS, objectName="simulation_status")
        self.status.setWordWrap(True)
        self.status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.status.setMinimumHeight(40)
        status_layout.addWidget(self.status)
        layout.addWidget(status_group)

        self.case_selector.currentIndexChanged.connect(self._apply_case)
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

    def _mark_custom(self) -> None:
        self.case_selector.setCurrentIndex(3)

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
        if index == 3:
            return
        for field, value in ((self.a1, float(index + 1)), (self.a0, 1.0)):
            field.blockSignals(True)
            field.setValue(value)
            field.blockSignals(False)
        self._reset_step()

    def input_state(self) -> LabInputs:
        try:
            if "," in self.t_end.text() or "," in self.t0.text():
                raise ValueError
            t_end = float(self.t_end.text())
            t0 = float(self.t0.text())
        except ValueError:
            raise ValueError("Enter numeric start/end times using a decimal point (for example 20.5).") from None
        return LabInputs(
            a1=self.a1.value(), a0=self.a0.value(), b0=self.b0.value(),
            t0=t0, t_end=t_end, dt=self.dt.value(),
            methods=tuple(key for key, check in self.method_checks.items() if check.isChecked()),
        )

    def _show_error(self, message: str) -> None:
        self.status.setText(f"Input error: {message}")

    def _refresh_feedback(self) -> None:
        try:
            self.input_state().validate()
        except ValueError as error:
            self._show_error(str(error))
            return
        self.status.setText(M1_STATUS)

    def _run_requested(self) -> None:
        self._refresh_feedback()
