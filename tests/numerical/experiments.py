"""Reproduce the report tables: python tests/numerical/experiments.py.

This script prints measured data; it does not change files or solver step sizes.
The explicit outer loop repeats each full simulation with half the previous h.
"""

import platform
from importlib.metadata import version
from math import exp, pi, sqrt

import numpy as np

from dss.analytical import solve_analytical
from dss.contracts import ModelParams, SimulationConfig
from dss.numerical import make_time_grid, solve_euler, solve_rk4


def convergence_table():
    print("\n## Additional convergence experiment")
    print("Model: a1=2, a0=1, b0=1; t_end=2. Reference: Word (9).")
    print("| Method | h | Endpoint y error | Previous error / error |")
    print("|---|---:|---:|---:|")
    expected = 1 - 3*exp(-2.)
    for solver in (solve_euler, solve_rk4):
        previous = None
        for h in (.1, .05, .025):
            t = make_time_grid(SimulationConfig(0., 2., h))
            result = solver(ModelParams(2., 1., 1.), t)
            error = abs(result.y[-1] - expected)
            ratio = "-" if previous is None else f"{previous/error:.6f}"
            print(f"| {result.method} | {h} | {error:.10e} | {ratio} |")
            previous = error


def halving_table():
    print("\n## Word task 5-7: repeated step halving")
    print("Examples: a1=1,2,3; a0=b0=1. Team choices: t_end=20, max y error <=0.01.")
    print("Reference: shared analytical solver for Word (8)-(10), on the identical grid.")
    print("| Case | Halvings | h | Samples | Euler max error | RK4 max error | Both <=0.01 |")
    print("|---|---:|---:|---:|---:|---:|---|")
    for case, a1 in enumerate((1., 2., 3.), start=1):
        model = ModelParams(a1, 1., 1.)
        h = .1 * 2*pi / sqrt(model.a0)
        for halvings in range(21):
            t = make_time_grid(SimulationConfig(0., 20., h))
            reference = solve_analytical(model, t)
            euler_error = np.max(abs(solve_euler(model, t).y - reference.y))
            rk4_error = np.max(abs(solve_rk4(model, t).y - reference.y))
            agreed = euler_error <= .01 and rk4_error <= .01
            print(f"| {case} | {halvings} | {h:.10f} | {len(t)} | "
                  f"{euler_error:.10e} | {rk4_error:.10e} | {'yes' if agreed else 'no'} |")
            if agreed:
                break
            h /= 2
        else:
            raise RuntimeError(f"Case {case} did not meet the team's error target")


if __name__ == "__main__":
    print("# Numerical experiments")
    print("Requirements source: original Lab1 RTS 09102026.doc; Markdown only assigns ownership.")
    print(f"Python {platform.python_version()}, {platform.system()}, NumPy {np.__version__}, "
          f"pytest {version('pytest')}")
    convergence_table()
    halving_table()
