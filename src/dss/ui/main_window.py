"""Frozen compact desktop presentation with real background calculation."""

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from dss.ui.colors import METHOD_COLORS
from dss.ui.execution import SimulationThread, make_request
from dss.ui.slider_input import SliderInput
from dss.ui.state import LabInputs
from dss.ui.theme import apply_theme, method_style, saved_theme, style_canvas, theme_settings
from dss.ui.presentation import prepare_results, retheme_results


class MainWindow(QMainWindow):
    def __init__(self, *, settings=None) -> None:
        super().__init__()
        self.settings = settings if settings is not None else theme_settings()
        self.theme_mode = saved_theme(self.settings)
        self.theme = apply_theme(QApplication.instance(), self.theme_mode)
        self.prepared_results = None
        self.last_responses = None
        self.last_run_inputs = None
        self._job = None
        self._pending_outcome = None
        self._input_revision = 0
        self._closing = False
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
        result_header = QHBoxLayout()
        result_header.addWidget(self._section("System Response"))
        result_header.addStretch()
        self.view_selector = QComboBox(objectName="plot_view")
        self.view_selector.addItems(["Response", "Error"])
        self.view_selector.setFixedWidth(108)
        self.view_selector.setEnabled(False)
        self.view_selector.setToolTip("Error view requires Exact and a numerical response on matching time grids.")
        result_header.addWidget(self.view_selector)
        self.export_png = QPushButton("PNG", objectName="export_png")
        self.export_pdf = QPushButton("PDF", objectName="export_pdf")
        for button in (self.export_png, self.export_pdf):
            button.setProperty("role", "step")
            button.setEnabled(False)
            button.setToolTip("Export is available after genuine simulation results are loaded.")
            result_header.addWidget(button)
        self.export_png.clicked.connect(self._export_png)
        self.export_pdf.clicked.connect(self._export_pdf)
        results.addLayout(result_header)
        self.plot_card = QFrame(objectName="plot_card")
        self.plot_layout = QVBoxLayout(self.plot_card)
        self.plot_layout.setContentsMargins(8, 8, 8, 8)
        self.legend_preview = QLabel(objectName="method_legend")
        self.legend_preview.setToolTip("Method identity preview; no simulation results loaded.")
        self.plot_layout.addWidget(self.legend_preview)
        self.figure = Figure(facecolor=self.theme.card, layout="constrained")
        self.figure.text(0.5, 0.5, "Simulation results will appear here", ha="center", va="center", fontsize=10, color=self.theme.secondary)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setObjectName("plot_placeholder")
        self.canvas.setMinimumSize(300, 240)
        self.plot_layout.addWidget(self.canvas, 1)
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
        self.view_selector.currentIndexChanged.connect(self._change_view)
        self._update_theme_widgets()

    def _toggle_theme(self) -> None:
        self.set_theme("dark" if self.theme_mode == "light" else "light")

    def set_theme(self, mode: str, *, persist: bool = True) -> None:
        self.theme = apply_theme(QApplication.instance(), mode)
        self.theme_mode = mode
        if persist:
            self.settings.setValue("ui/theme", mode)
            self.settings.sync()
        if self.prepared_results is not None:
            try:
                prepared = retheme_results(self.prepared_results, mode)
            except Exception as error:
                self._clear_results()
                self._set_status(f"Visualization failed: {error}", "error")
            else:
                self.prepared_results = prepared
                self._change_view(self.view_selector.currentIndex())
        self._update_theme_widgets()

    def _update_theme_widgets(self) -> None:
        target = "Dark" if self.theme_mode == "light" else "Light"
        self.theme_toggle.setText("☾" if self.theme_mode == "light" else "☀")
        self.theme_toggle.setToolTip(f"Switch to {target} Mode")
        self.theme_toggle.setAccessibleName(f"Switch to {target} Mode")
        for method, check in self.method_checks.items():
            check.setStyleSheet(method_style(method, self.theme_mode))
        figures = [self.figure] if self.prepared_results is None else [
            self.prepared_results.response_figure, self.prepared_results.error_figure
        ]
        for figure in figures:
            if figure is not None:
                figure.set_facecolor(self.theme.card)
        if self.prepared_results is None:
            for text in self.figure.texts:
                text.set_color(self.theme.secondary)
        self._update_legend()
        style_canvas(self.canvas, self.theme)
        self.canvas.draw_idle()

    def _update_legend(self) -> None:
        methods = self.prepared_results.methods if self.prepared_results else tuple(
            key for key, check in self.method_checks.items() if check.isChecked()
        )
        names = {"analytical": "Exact", "euler": "Euler", "rk4": "RK4"}
        self.legend_preview.setText(" &nbsp; ".join(
            f'<span style="color:{METHOD_COLORS[key]}">●</span> {names[key]}' for key in methods
        ))

    def _replace_figure(self, figure: Figure) -> None:
        old_canvas = self.canvas
        old_figure = self.figure
        self.plot_layout.removeWidget(old_canvas)
        old_canvas.hide()
        # QtAgg's queued zero-delay draw can outlive canvas replacement. Cancel
        # that pending draw before detaching the figure (not an active render).
        old_canvas._draw_pending = False
        old_canvas.close()
        if old_figure.canvas is old_canvas:
            old_figure.set_canvas(None)
        old_canvas.deleteLater()
        self.figure = figure
        self.canvas = FigureCanvasQTAgg(figure)
        self.canvas.setObjectName("plot_placeholder")
        self.canvas.setMinimumSize(300, 240)
        self.plot_layout.addWidget(self.canvas, 1)
        self._update_theme_widgets()

    def show_responses(self, responses: list, *, api=None) -> bool:
        """M4 handoff: accept shared Responses; never run solvers here."""
        try:
            prepared = prepare_results(responses, api, theme=self.theme_mode)
        except Exception as error:
            self._clear_results()
            self._set_status(f"Visualization failed: {error}", "error")
            return False
        self.prepared_results = prepared
        self.view_selector.blockSignals(True)
        self.view_selector.setCurrentIndex(0)
        self.view_selector.blockSignals(False)
        self.view_selector.setEnabled(prepared.error_figure is not None)
        self._replace_figure(prepared.response_figure)
        self.export_png.setEnabled(True)
        self.export_pdf.setEnabled(True)
        names = {"euler": "Euler", "rk4": "RK4"}
        self.metrics.setText("\n".join(
            f"{names[key]}   Max |error|: {value.max_abs:.6g}   RMSE: {value.rmse:.6g}"
            for key, value in prepared.metrics.items()
        ) or "Not calculated — Exact and a numerical response are required.")
        self.legend_preview.setToolTip("Methods in the loaded simulation results.")
        self._set_status("Simulation completed. Results loaded.")
        return True

    def _clear_results(self) -> None:
        self.prepared_results = None
        self.view_selector.blockSignals(True)
        self.view_selector.setCurrentIndex(0)
        self.view_selector.blockSignals(False)
        self.view_selector.setEnabled(False)
        self.export_png.setEnabled(False)
        self.export_pdf.setEnabled(False)
        self.metrics.setText("No results yet")
        self.legend_preview.setToolTip("Method identity preview; no simulation results loaded.")
        placeholder = Figure(facecolor=self.theme.card, layout="constrained")
        placeholder.text(0.5, 0.5, "Simulation results will appear here", ha="center", va="center", fontsize=10, color=self.theme.secondary)
        self._replace_figure(placeholder)

    def _change_view(self, index: int) -> None:
        if self.prepared_results is None:
            return
        figure = self.prepared_results.error_figure if index else self.prepared_results.response_figure
        if figure is not None:
            self._replace_figure(figure)

    def _export_png(self) -> None:
        self.export_current("png")

    def _export_pdf(self) -> None:
        self.export_current("pdf")

    def export_current(self, suffix: str) -> None:
        from pathlib import Path
        if self.prepared_results is None:
            self._set_status("Export requires simulation results.", "notice")
            return
        if suffix not in ("png", "pdf"):
            self._show_error("Choose PNG or PDF export.")
            return
        name, _ = QFileDialog.getSaveFileName(
            self, "Export current plot", f"{self.view_selector.currentText().lower()}.{suffix}",
            f"{suffix.upper()} (*.{suffix})", options=QFileDialog.Option.DontConfirmOverwrite,
        )
        if not name:
            return
        path = Path(name)
        if not path.suffix:
            path = path.with_suffix(f".{suffix}")
        if path.suffix.lower() != f".{suffix}":
            self._show_error(f"Choose a .{suffix} file for this export.")
            return
        if path.exists() and QMessageBox.question(
            self, "Replace file?", f"Replace {path.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            self.prepared_results.api.export_figure(self.figure, path)
            if not path.is_file() or path.stat().st_size == 0:
                raise OSError("The exporter did not create a nonempty selected file.")
        except Exception as error:
            self._show_error(f"Export failed: {error}")
            return
        self._set_status(f"Exported {path.name}")

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
        if self._job is not None:
            message = "Finishing calculation before closing..." if self._closing else f"Calculating... Input error: {message}"
            self._set_status(message, "notice")
            return
        self._set_status(f"Input error: {message}", "error")

    def _refresh_feedback(self) -> bool:
        self._input_revision += 1
        self.last_responses = None
        self.last_run_inputs = None
        if self.prepared_results is not None:
            self._clear_results()
        self._update_legend()
        if self._job is not None:
            message = "Finishing calculation before closing..." if self._closing else "Calculating... Inputs changed; results will be discarded."
            self._set_status(message, "notice")
            return False
        try:
            self.input_state().validate()
        except ValueError as error:
            self._show_error(str(error))
            return False
        self._set_status("Ready to simulate")
        return True

    def _run_requested(self) -> None:
        if self._job is not None or self._closing:
            return
        self.last_responses = None
        self.last_run_inputs = None
        if self.prepared_results is not None:
            self._clear_results()
        self._update_legend()
        try:
            request = make_request(self.input_state(), self._input_revision)
        except Exception as error:
            self._show_error(str(error))
            return
        self._job = SimulationThread(request, self)
        self._pending_outcome = None
        self._job.outcome_ready.connect(self._record_outcome)
        self._job.finished.connect(self._execution_finished)
        self.run_button.setEnabled(False)
        self._set_status("Calculating...", "notice")
        self._job.start()

    @Slot(object)
    def _record_outcome(self, outcome) -> None:
        # Queued to the GUI thread. Do not enable another run before finished.
        self._pending_outcome = outcome

    @Slot()
    def _execution_finished(self) -> None:
        job = self._job
        if job is None:
            return
        # Only wait AFTER Qt's finished signal; there is no active solver wait
        # on the GUI thread. This also joins final native thread cleanup.
        job.wait()
        request = job.request
        outcome = self._pending_outcome or job.outcome
        self._job = None
        self._pending_outcome = None
        job.outcome = None
        job.deleteLater()
        self.run_button.setEnabled(not self._closing)
        if self._closing:
            self.last_responses = None
            self.last_run_inputs = None
            self.close()
            return
        try:
            current = self._input_revision == request.revision and self.input_state() == request.inputs
        except ValueError:
            current = False
        if not current:
            self._set_status("Calculation finished; inputs changed, results discarded.", "notice")
        elif outcome is None:
            self._set_status("Calculation failed without a result.", "error")
        elif outcome.error is not None:
            self._set_status(f"Calculation failed: {outcome.error}", "error")
        else:
            self.last_responses = outcome.responses
            self.last_run_inputs = request.inputs
            self.show_responses(outcome.responses)

    def closeEvent(self, event) -> None:
        if self._job is not None:
            self._closing = True
            self._set_status("Finishing calculation before closing...", "notice")
            event.ignore()
            return
        self.last_responses = None
        self.last_run_inputs = None
        super().closeEvent(event)
