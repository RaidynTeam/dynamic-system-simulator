"""PySide6 presentation layer for the instructor's lab model."""

from PySide6.QtCore import QLocale, Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QMainWindow, QPushButton,
    QScrollArea, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from dss.ui.controller import M1_STATUS
from dss.ui.state import LabInputs


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
        layout.addWidget(QLabel("CMPE 443 · Lab 1    |    M1 — UI skeleton"))
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
        self.a1 = self._number("a1", 1.0)
        self.a0 = self._number("a0", 1.0)
        self.b0 = self._number("b0", 1.0)
        for label, field in (("a₁", self.a1), ("a₀", self.a0), ("b₀ (step gain)", self.b0)):
            form.addRow(label, field)
        fixed = QLabel("API mapping: a₂ = 1, u₀ = b₀\ny₀ = 0, v₀ = 0, t₀ = 0")
        fixed.setWordWrap(True)
        form.addRow(fixed)
        left.addWidget(model)

        simulation = QGroupBox("Simulation configuration")
        config = QFormLayout(simulation)
        self.t_end = self._number("t_end", 20.0)
        self.t_end.setToolTip("UI default: 20 seconds; choose the desired observation interval.")
        self.dt = self._number("dt", LabInputs.initial_step(1.0))
        config.addRow("End time (s)", self.t_end)
        config.addRow("Time step Δt (s)", self.dt)
        reset = QPushButton("Reset Δt to lab initial value", objectName="reset_dt")
        reset.clicked.connect(self._reset_step)
        config.addRow(reset)
        note = QLabel("Initial Δt = 0.1 × 2π / √a₀.\nReduce Δt later to compare numerical and exact results.")
        note.setWordWrap(True)
        config.addRow(note)
        left.addWidget(simulation)

        methods = QGroupBox("Methods")
        method_layout = QHBoxLayout(methods)
        self.method_checks = {}
        for key, label in (("analytical", "Exact"), ("euler", "Euler"), ("rk4", "RK4")):
            check = QCheckBox(label, objectName=f"method_{key}")
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
            0.5, 0.5, "Plot placeholder\nNo simulation results — M1 skeleton",
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

    @staticmethod
    def _number(name: str, value: float) -> QDoubleSpinBox:
        field = QDoubleSpinBox(objectName=name)
        field.setLocale(QLocale.c())
        field.setDecimals(8)
        field.setRange(0.00000001, 1_000_000.0)
        field.setValue(value)
        field.setKeyboardTracking(False)
        return field

    def _mark_custom(self) -> None:
        self.case_selector.setCurrentIndex(3)

    def _a0_changed(self) -> None:
        self._mark_custom()
        self._reset_step()

    def _reset_step(self) -> None:
        self.dt.setValue(LabInputs.initial_step(self.a0.value()))

    def _apply_case(self, index: int) -> None:
        if index == 3:
            return
        for field, value in ((self.a1, float(index + 1)), (self.a0, 1.0)):
            field.blockSignals(True)
            field.setValue(value)
            field.blockSignals(False)
        self._reset_step()

    def input_state(self) -> LabInputs:
        for field in (self.a1, self.a0, self.b0, self.t_end, self.dt):
            field.interpretText()
        return LabInputs(
            a1=self.a1.value(), a0=self.a0.value(), b0=self.b0.value(),
            t_end=self.t_end.value(), dt=self.dt.value(),
            methods=tuple(key for key, check in self.method_checks.items() if check.isChecked()),
        )

    def _run_requested(self) -> None:
        try:
            self.input_state().validate()
        except ValueError as error:
            self.status.setText(f"Input error: {error}")
            return
        self.status.setText(M1_STATUS)
