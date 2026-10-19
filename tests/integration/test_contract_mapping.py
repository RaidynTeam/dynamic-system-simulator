"""Check the merged v0.2 contract without wiring any real simulation."""

from dss.contracts import ModelParams, SimulationConfig
from dss.ui.state import LabInputs


def test_form_maps_to_current_shared_contract_and_preserves_legacy_mapping():
    inputs = LabInputs(a1=3, a0=1, b0=2.5)
    model = ModelParams(**inputs.lab_model_kwargs())
    config = SimulationConfig(**inputs.config_kwargs())
    assert (model.a1, model.a0, model.b0) == (3, 1, 2.5)
    assert (config.t0, config.t_end, config.dt) == (0, inputs.t_end, inputs.dt)
    assert inputs.model_kwargs() == dict(a2=1, a1=3, a0=1, u0=2.5, y0=0, v0=0)
