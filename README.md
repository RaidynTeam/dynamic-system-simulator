# Dynamic System Simulator

**An academic desktop application for exploring second-order dynamic systems.**

Dynamic System Simulator models the unit-step response of a linear second-order
system and compares its exact analytical solution with two numerical methods:
Forward Euler and fourth-order Runge–Kutta (RK4). An interactive Python interface
lets users change model parameters, adjust the time step, compare response and
error plots, and export figures for laboratory analysis.

## Academic Context

This project was developed by **RaidynTeam** for **Lab 1 — Modeling of Dynamic
System Response on Unit Step Input**, as part of **CMPE 443 / CMSE 443 — Real-Time
System Design** at **Eastern Mediterranean University**, Department of Computer
Engineering, in the **Fall 2026–2027** semester.

| Teaching role | Name and academic title |
| --- | --- |
| Course lecturer | [Prof. Dr. Alexander Chefranov](https://cmpe.emu.edu.tr/en/about-us/staff/staff-detail?n=alexander-chefranov&sid=222), Distinguished Professor |
| Laboratory instructor | [Reza Asar](https://cmpe.emu.edu.tr/en/about-us/staff/staff-detail?n=reza-asar&sid=309), Research Assistant |

The work connects continuous-time system models with discrete-time computation.
Its purpose is to investigate how damping and sampling choices affect a simulated
response, and how numerical results compare with an analytical reference. It also
provides practical experience in scientific programming, modular software design,
and collaborative engineering.


## The System Model

The simulator solves the differential equation

$$
\frac{d^2y}{dt^2} + a_1\frac{dy}{dt} + a_0 y = b_0 u(t),
\qquad y(0)=0,\quad y'(0)=0,
$$

where $u(t)=1$ for $t\geq0$ and $a_1$, $a_0$, and $b_0$ are positive model
parameters. Here, $y(t)$ is the system output, $a_1$ determines the damping term,
$a_0$ determines the natural frequency $\omega_n=\sqrt{a_0}$, and $b_0$ scales the
input. The steady-state output is $b_0/a_0$.

The characteristic equation, $s^2+a_1s+a_0=0$, defines three response types:

| Preset | Parameters | Response type | Characteristic roots |
| --- | --- | --- | --- |
| Case 1 | $a_1=1$, $a_0=1$ | Underdamped | Complex conjugate roots |
| Case 2 | $a_1=2$, $a_0=1$ | Critically damped | A repeated real root |
| Case 3 | $a_1=3$, $a_0=1$ | Overdamped | Two distinct real roots |

Users can also explore custom positive coefficients. The presets retain the
selected input gain $b_0$.

## Methods and Features

| Method | Purpose |
| --- | --- |
| **Exact** | Evaluates the analytical solution for the system's damping case and supplies a reference for error analysis. |
| **Euler** | Approximates the response using first-order Forward Euler integration. |
| **RK4** | Approximates the response using the classical fourth-order Runge–Kutta method. |

All selected methods use the same time grid so their results can be compared
directly. The application provides:

- Interactive controls for coefficients, simulation duration, and time step.
- Three damping presets and support for custom parameter combinations.
- Response curves for any selected combination of Exact, Euler, and RK4.
- Absolute-error plots, maximum absolute error, and root mean square error (RMSE)
  when Exact and at least one numerical method are selected together.
- Automatic initial time-step selection using
  $\Delta t=0.1\cdot2\pi/\sqrt{a_0}$, with manual adjustment and step-halving controls.
- Light and dark themes, plus PNG and PDF export of the selected plot.
- Background solver execution to keep the interface available during computation.

The automatic time step is a starting point for comparison. Reduce it and rerun
the simulation to investigate numerical accuracy and stability.

## Contributors

The application was built collaboratively by four team members. Their primary
contributions are listed below.

| Contributor | Primary contributions |
| --- | --- |
| [Kerem Boylu](https://github.com/KEREMBOYLU) | Analytical solutions, damping classification, shared model contracts, and initial project setup. |
| [Ekrem Cantürk](https://github.com/code-eko) | Numerical integration with Euler and RK4, shared time-grid generation, packaging, and continuous integration. |
| [Furkan Nişancı](https://github.com/furkanisanci) | PySide6 interface, parameter controls, themes, background execution, and integration of solvers with plots. |
| [Selver Kıskaç](https://github.com/slvrkskc) | Response and error visualization, error metrics, figure styling, and PNG/PDF export. |

## Installation

Use **Python 3.11**, the version used for the project's verification and CI.
The application uses **NumPy**, **PySide6**, and **Matplotlib**; the installation
commands below install these dependencies automatically. A desktop session is
required to display the interface.

First, clone the repository and enter its directory:

```sh
git clone https://github.com/RaidynTeam/dynamic-system-simulator.git
cd dynamic-system-simulator
```

### macOS and Linux

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m dss
```

For later sessions, run these commands from the project directory:

```sh
source .venv/bin/activate
python -m dss
```

If macOS reports that the Qt `cocoa` platform plugin cannot be initialized and
the environment's Qt files are marked hidden, clear that flag and try again:

```sh
/usr/bin/chflags -R nohidden .venv
.venv/bin/python -m dss
```

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m dss
```

For later sessions, run `.\.venv\Scripts\python.exe -m dss` from the project
directory.

### Visual Studio Code

Open the project folder and select the Python interpreter inside `.venv` using
**Python: Select Interpreter**. In the integrated terminal, run the appropriate
launch command above. The application entry point is the `dss` module, launched
with `python -m dss`.

## Using the Simulator

1. Choose **Case 1**, **Case 2**, or **Case 3**, or adjust the model coefficients.
2. Set the input gain $b_0$, simulation end time, and time step. Leave **Auto dt**
   enabled to use the initial step from the lab formula.
3. Select **Exact**, **Euler**, and/or **RK4**, then click **Run Simulation**.
4. Compare the curves in **Response**. Select **Error** to inspect deviations
   from Exact and read the error metrics.
5. Reduce the time step and run again to observe how the numerical approximations
   change.
6. Use **PNG** or **PDF** to save the currently selected plot.

For error analysis, include **Exact** together with Euler or RK4. Otherwise, the
error view is unavailable and metrics remain **Not calculated**. Changing inputs
invalidates the previous results; run the simulation again for the new settings.

## Project Structure

```text
src/dss/
├── __main__.py       # Desktop application entry point
├── contracts.py      # Shared models, response types, and validation
├── analytical/       # Damping classification and exact solutions
├── numerical/        # Time grid, Euler, and RK4 solvers
├── ui/               # Interface, controller, and background execution
└── visualization/    # Response plots, error metrics, and figure export
tests/               # Automated tests
docs/                # Laboratory reference and technical documentation
```

## Verification

Install the optional test dependencies:

```sh
python -m pip install -e ".[dev]"
```

Run the suite without displaying application windows:

```sh
QT_QPA_PLATFORM=offscreen MPLBACKEND=Agg python -m pytest -q
```

On Windows PowerShell:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
$env:MPLBACKEND = "Agg"
.\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:QT_QPA_PLATFORM
Remove-Item Env:MPLBACKEND
```

The suite covers model validation, analytical solutions, numerical methods,
plotting, error metrics, exports, and interface integration. GitHub Actions runs
the tests on Windows with Python 3.11.

## License

This project is distributed under the [MIT License](LICENSE).
