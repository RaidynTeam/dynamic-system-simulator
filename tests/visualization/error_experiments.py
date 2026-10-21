"""Measure how the error falls as the step is halved:

    python tests/visualization/error_experiments.py

Prints a Markdown record and changes nothing. Every number comes from running
the real solvers through the real compute_error; nothing here is a prediction.

The step starts at the handout's T = 0.1 * 2 * pi / sqrt(a0) and is halved five
times. The "ratio" column is the previous level's error divided by this one, so
it shows the observed order of each method rather than asserting it: a first
order method is expected near 2 and a fourth order one near 16.
"""

import platform
import sys
from importlib.metadata import version
from math import pi, sqrt

from dss.analytical import solve_analytical
from dss.contracts import ModelParams, SimulationConfig
from dss.numerical import make_time_grid, solve_euler, solve_rk4
from dss.visualization import compute_error

T_END = 20.0
LEVELS = 6  # h0 down to h0/32
CASES = ((1, 1.0), (2, 2.0), (3, 3.0))
SOLVERS = (("euler", solve_euler), ("rk4", solve_rk4))


def environment():
    print("## Environment")
    print()
    # platform.release() still says "10" on Windows 11, so print the build
    # instead of a version number that would be wrong.
    print(f"- Python {platform.python_version()} on {platform.system()} build {platform.version()}")
    for package in ("numpy", "matplotlib"):
        print(f"- {package} {version(package)}")
    print(f"- Interpreter: {sys.executable}")
    print()


def table(case, a1):
    model = ModelParams(a1=a1, a0=1.0, b0=1.0)
    initial = 0.1 * 2 * pi / sqrt(model.a0)

    print(f"### Case {case}: a1={a1:g}, a0=1, b0=1, t0=0, t_end={T_END:g} s")
    print()
    print(f"Initial step T = 0.1*2*pi/sqrt(a0) = {initial:.10f} s")
    print()
    print("| Step | dt (s) | N | Method | max abs error | RMSE | previous/this |")
    print("|---|---:|---:|---|---:|---:|---:|")

    previous = {name: None for name, _ in SOLVERS}
    for level in range(LEVELS):
        divisor = 2**level
        step = initial / divisor
        t = make_time_grid(SimulationConfig(t0=0.0, t_end=T_END, dt=step))
        exact = solve_analytical(model, t)
        label = "h0" if divisor == 1 else f"h0/{divisor}"
        for name, solver in SOLVERS:
            metrics = compute_error(exact, solver(model, t))
            earlier = previous[name]
            ratio = "-" if earlier is None else f"{earlier / metrics.max_abs:.2f}"
            print(
                f"| {label} | {step:.10f} | {t.size} | {name} "
                f"| {metrics.max_abs:.10e} | {metrics.rmse:.10e} | {ratio} |"
            )
            previous[name] = metrics.max_abs
    print()


def main():
    print("# Visualization error experiments")
    print()
    print(
        "Measured by running tests/visualization/error_experiments.py. The"
        " reference is Person 1's solve_analytical; the candidates are Person"
        " 2's solve_euler and solve_rk4; the metric is Person 4's compute_error."
        " All three solvers receive the same time grid from Person 2's"
        " make_time_grid, so no interpolation is involved."
    )
    print()
    environment()
    for case, a1 in CASES:
        table(case, a1)
    print("Each run uses b0 = 1 and t_end = 20 s. Those are team choices, not")
    print("values the handout fixes; the handout fixes only the initial step and")
    print("the (a1, a0) pairs that select the three cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
