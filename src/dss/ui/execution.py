"""Immutable run requests and a Qt worker; all mathematics stays in controller."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtCore import QThread, Signal

from dss.ui.state import LabInputs

if TYPE_CHECKING:
    from dss.contracts import ModelParams, Response, SimulationConfig


@dataclass(frozen=True)
class RunRequest:
    inputs: LabInputs
    model: ModelParams
    config: SimulationConfig
    revision: int


def make_request(inputs: LabInputs, revision: int) -> RunRequest:
    from dss.contracts import ModelParams, SimulationConfig

    inputs.validate()
    return RunRequest(
        inputs, ModelParams(**inputs.lab_model_kwargs()),
        SimulationConfig(**inputs.config_kwargs()), revision,
    )


@dataclass(frozen=True)
class RunOutcome:
    responses: tuple[Response, ...] | None = None
    error: Exception | None = None


class SimulationThread(QThread):
    """One bounded job; no Qt widgets, visualization, cancellation or retries."""

    outcome_ready = Signal(object)

    def __init__(self, request: RunRequest, parent=None):
        super().__init__(parent)
        self.request = request
        self.outcome: RunOutcome | None = None

    def run(self) -> None:
        try:
            from dss.ui.controller import run_simulation
            responses = run_simulation(self.request.model, self.request.config, self.request.inputs.methods)
            self.outcome = RunOutcome(responses=tuple(responses))
        except Exception as error:
            # Preserve the actual exception, not a rewritten worker exception.
            self.outcome = RunOutcome(error=error)
        self.outcome_ready.emit(self.outcome)
