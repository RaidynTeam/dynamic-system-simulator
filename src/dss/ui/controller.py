"""Reserved integration boundary. Real solver orchestration is outside M1."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dss.contracts import ModelParams, Response, SimulationConfig


M1_STATUS = (
    "M1 skeleton: simulation is unavailable until the shared solvers are "
    "integrated. No results have been calculated."
)


def run_simulation(
    model: ModelParams, config: SimulationConfig, methods: tuple[str, ...]
) -> list[Response]:
    """Keep the agreed signature without importing unfinished implementations."""
    raise NotImplementedError(M1_STATUS)
