"""UI input state; no Qt, solvers, or replacement shared contract types."""

from dataclasses import dataclass
from math import ceil, isfinite, pi, sqrt


@dataclass(frozen=True)
class LabInputs:
    """A snapshot of the lab form, not a general ModelParams validator."""

    a1: float = 1.0
    a0: float = 1.0
    b0: float = 1.0
    t_end: float = 20.0  # UI convenience, not an instructor requirement.
    dt: float = 0.2 * pi
    methods: tuple[str, ...] = ("analytical", "euler", "rk4")
    t0: float = 0.0

    @staticmethod
    def initial_step(a0: float) -> float:
        return 0.1 * 2 * pi / sqrt(a0)

    def validate(self) -> None:
        if not isfinite(self.t0) or self.t0 != 0:
            raise ValueError("Start time must be zero for the lab unit-step model.")
        for name in ("a1", "a0", "b0", "t_end", "dt"):
            value = getattr(self, name)
            if not isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and greater than zero.")
        if self.t_end <= self.t0:
            raise ValueError("End time must be greater than start time.")
        estimated_steps = (self.t_end - self.t0) / self.dt
        if not isfinite(estimated_steps) or ceil(estimated_steps) + 1 > 1_000_000:
            raise ValueError("Configuration exceeds 1,000,000 samples; increase dt or reduce end time.")
        if not self.methods:
            raise ValueError("Select at least one method.")
        if len(set(self.methods)) != len(self.methods) or any(
            method not in ("analytical", "euler", "rk4") for method in self.methods
        ):
            raise ValueError("Select distinct Exact, Euler, or RK4 methods.")

    def model_kwargs(self) -> dict[str, float]:
        """Legacy general ModelParams fields requested in the M1 task (v0.1)."""
        return dict(a2=1.0, a1=self.a1, a0=self.a0, u0=self.b0, y0=0.0, v0=0.0)

    def lab_model_kwargs(self) -> dict[str, float]:
        """Fields for the team's merged lab ModelParams contract (v0.2)."""
        return dict(a1=self.a1, a0=self.a0, b0=self.b0)

    def config_kwargs(self) -> dict[str, float]:
        """Future SimulationConfig(**inputs.config_kwargs())."""
        return dict(t0=self.t0, t_end=self.t_end, dt=self.dt)
