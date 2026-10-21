"""Render the real comparison figures to look at them: python tests/visualization/preview.py

Automated tests check numbers, labels and object identity; they cannot tell you
whether a figure is readable. This script builds the production figure from the
real solvers and writes PNGs for a human to inspect.

The six scenarios are the ones Person 2 proposed for the report screenshots in
docs/modules/numerical-handoff.md, so what you see here is what the report will
show once Person 3's M4B-2 integration is in place.

Output goes to a temporary folder by default, never into the repository. Pass a
directory to put the files somewhere else, and --open to open the folder.

    python tests/visualization/preview.py
    python tests/visualization/preview.py C:\\Users\\me\\Desktop\\m2-preview --open
    python tests/visualization/preview.py --theme dark
"""

import argparse
import os
import platform
import subprocess
import sys
import tempfile
from math import pi, sqrt
from pathlib import Path

from matplotlib.backends.backend_agg import FigureCanvasAgg

from dss.analytical import solve_analytical
from dss.contracts import ModelParams, SimulationConfig
from dss.numerical import make_time_grid, solve_euler, solve_rk4
from dss.visualization import build_response_figure

T_END = 20.0

# (case, a1, step divisor). The handout's initial step is 0.1*2*pi/sqrt(a0);
# the divisors are the refinements Person 2 measured for the report.
SCENARIOS = (
    (1, 1.0, 1),
    (1, 1.0, 32),
    (2, 2.0, 1),
    (2, 2.0, 16),
    (3, 3.0, 1),
    (3, 3.0, 8),
)


def render(case, a1, divisor, theme, directory):
    model = ModelParams(a1=a1, a0=1.0, b0=1.0)
    step = (0.1 * 2 * pi / sqrt(model.a0)) / divisor
    t = make_time_grid(SimulationConfig(t0=0.0, t_end=T_END, dt=step))
    responses = [
        solve_analytical(model, t),
        solve_euler(model, t),
        solve_rk4(model, t),
    ]
    label = "h0" if divisor == 1 else f"h0 over {divisor}"
    title = f"Case {case}   a1={a1:g}  a0=1  b0=1   dt={step:.6f} s   N={t.size}"
    figure = build_response_figure(responses, theme=theme, title=title)
    FigureCanvasAgg(figure).draw()

    name = f"case{case}-{label.replace(' ', '')}-{theme}.png"
    path = directory / name
    figure.savefig(path, dpi=110, facecolor=figure.get_facecolor())
    print(f"{path.name:34} Case {case}  dt={step:.6f}  N={t.size}  {theme}")
    return path


def open_folder(directory):
    system = platform.system()
    if system == "Windows":
        os.startfile(directory)  # noqa: S606 - local developer convenience only
    elif system == "Darwin":
        subprocess.run(["open", str(directory)], check=False)
    else:
        subprocess.run(["xdg-open", str(directory)], check=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "directory",
        nargs="?",
        help="where to write the PNGs (default: a folder in the system temp directory)",
    )
    parser.add_argument(
        "--theme",
        choices=("light", "dark", "both"),
        default="both",
        help="which theme to render (default: both)",
    )
    parser.add_argument("--open", action="store_true", help="open the folder afterwards")
    arguments = parser.parse_args(argv)

    directory = Path(
        arguments.directory
        if arguments.directory
        else Path(tempfile.gettempdir()) / "dss-visualization-preview"
    )
    directory.mkdir(parents=True, exist_ok=True)

    themes = ("light", "dark") if arguments.theme == "both" else (arguments.theme,)
    print(f"Writing to {directory}\n")
    for theme in themes:
        for case, a1, divisor in SCENARIOS:
            render(case, a1, divisor, theme, directory)

    print(
        "\nWhat to check: all three curves distinguishable by colour and line style;"
        "\nthe Exact curve still visible under RK4; markers readable rather than a"
        "\nsolid band; title, axis labels and legend not clipped or overlapping data."
        "\nThese are development renders, not report evidence."
    )
    if arguments.open:
        open_folder(directory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
