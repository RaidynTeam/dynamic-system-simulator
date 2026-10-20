"""M1 acceptance: the module builds figures with no pyplot, Qt or GUI backend.

Run in a subprocess because `sys.modules` in the pytest process is already
polluted by the UI test suite, which imports PySide6 and the Qt backend.
"""

import json
import os
import pathlib
import subprocess
import sys

import dss

SRC = str(pathlib.Path(dss.__file__).resolve().parent.parent)

FORBIDDEN_ROOTS = ("PySide6", "shiboken6", "PyQt5", "PyQt6")

PROBE = """
import json, sys

import dss.demo_data as demo
import dss.visualization as viz

figure = viz.new_figure("dark")
axes = figure.add_subplot()
for response in demo.make_demo_responses():
    axes.plot(response.t, response.y, **viz.plot_kwargs(response.method, "dark"))
axes.legend()
viz.style_axes(axes, "dark")
viz.apply_figure_theme(figure, "light")

forbidden = {forbidden!r}
leaked = sorted(
    name
    for name in sys.modules
    if name == "matplotlib.pyplot" or name.split(".")[0] in forbidden
)
backend = sorted(
    name for name in sys.modules if name.startswith("matplotlib.backends")
)
print(json.dumps({{"leaked": leaked, "backends": backend, "axes": len(figure.axes)}}))
""".format(forbidden=FORBIDDEN_ROOTS)


def _run_probe():
    environment = dict(os.environ)
    environment["PYTHONPATH"] = SRC
    # No MPLBACKEND: selecting a backend must not be necessary to build a figure.
    environment.pop("MPLBACKEND", None)
    environment.pop("QT_QPA_PLATFORM", None)
    result = subprocess.run(
        [sys.executable, "-c", PROBE],
        capture_output=True,
        text=True,
        env=environment,
        timeout=180,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_building_a_figure_imports_neither_pyplot_nor_qt():
    report = _run_probe()
    assert report["leaked"] == []


def test_building_a_figure_selects_no_interactive_backend():
    report = _run_probe()
    assert all("qt" not in name.lower() for name in report["backends"])
    assert report["axes"] == 1
