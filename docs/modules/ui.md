# UI — Person 3, M1

## Scope and source

M1 provides a PySide6 window and event loop, not simulation integration.
The instructor's **Lab1 RTS 09102026** handout is absent locally and in the
checked-out repository. Only the user's verified requirements are used:
unit step, zero initial conditions, positive a1/a0/b0, Cases (1,1), (2,1),
(3,1), and initial dt = 0.1 * 2*pi/sqrt(a0). Deadline, report requirements,
physical coefficient units, and any additional academic behavior are unverified.
The existing lab-requirements file and shared contract are owned by Person 1
and have not been changed. The task's verified cases supersede older warnings
in the team guides about unknown case definitions for this M1 UI only.

## Architecture

- `dss.__main__.main`: owns QApplication, shows MainWindow, returns event-loop exit code.
- `ui/main_window.py`: widgets, case controls, input snapshot, status presentation,
  and a single FigureCanvasQTAgg containing placeholder text. No computed curves.
- `ui/state.py`: immutable LabInputs form snapshot with no Qt dependency.
  It represents the restricted lab form, not a duplicate shared contract.
- `ui/controller.py`: retains the agreed run_simulation signature, using type-only
  imports. It explicitly raises NotImplementedError in M1. The form does not
  call it with fabricated contract objects. No shared module is imported at startup.

Future adapters can construct `ModelParams(**inputs.model_kwargs())` and
`SimulationConfig(**inputs.config_kwargs())` once those types exist:

| Lab form | General API v0.1 |
|---|---|
| a1, a0 | a1, a0 |
| b0 | u0 |
| Fixed normalization | a2 = 1 |
| Fixed initial conditions | y0 = 0, v0 = 0, t0 = 0 |
| End time, dt | t_end, dt |
| Exact / Euler / RK4 | analytical / euler / rk4 |

No shared API change is required or proposed. Positive lab input bounds are UI
constraints; they do not narrow the team's general ModelParams contract.
Full parsing/validation integration is deferred to M2. Numeric widgets use C locale,
eight decimals and positive bounds [1e-8, 1e6]; these are UI limits, not lab claims.
The displayed dt is rounded to eight decimals. Case selection resets a1/a0 and dt,
preserves b0, and does not calculate a response. Editing a1/a0 selects Custom;
editing a0 resets dt to the lab initial value. dt can then be reduced manually.
Defaults b0=1 and t_end=20 seconds are UI conveniences, not instructor requirements.

Run Simulation validates the form snapshot and displays M1 unavailability, or
an input message for empty methods. The canvas and metric cells stay empty / Not
calculated. No DEMO data, zero-error claims, exports, workers, solvers or algorithm
implementations are included. Use the UI with `python -m dss`.

## Verification and handoff

- Shared contract: ORTAK-SOZLESME-v0.1, unchanged; contract types not implemented.
- Branch: `feat/ui-m1`; commit identifiers are available in Git history and the PR.
- Implemented milestone: M1 UI skeleton only; M2 is not started.
- Tests and actual results (2026-10-19): editable package install succeeded in
  local Python 3.11.17; PySide6 6.12.0, Matplotlib 3.11.2, pytest 9.1.1.
  `python -m pytest -q`: 10 passed. Covers open/close, required controls,
  presets/API mapping, initial dt/refinement, empty methods/status, minimum size,
  unavailable controller, and isolated real entry point with all unfinished
  shared module imports explicitly blocked. `git diff --check` passed.
- Automated native Windows smoke: startup, Case 3, Run status and close passed.
  Native renders at 1120x800 and 940x700 logical pixels inspected visually.
  The input pane scrolls at minimum size; Run stays visible below it.
  Offscreen Windows Qt exposes no fonts on this machine, so its pixel renders
  show missing glyphs; native Windows uses Segoe UI and renders readable text.
  Screenshots are local ignored verification artifacts under `.venv/`.
- Desktop/manual record: no human interactive desktop acceptance test performed.
  Headless lifecycle checks do not replace human desktop review.
- Next task: team review of M1. Obtain the instructor handout and have Person 1
  reconcile docs/lab-requirements.md. Begin M2 only with user approval.
- Integration dependencies: Person 1 ModelParams/SimulationConfig/Response and
  validators; Person 2 shared time grid and numerical solvers; Person 1 analytical
  solver; Person 4 Figure/metrics functions. They are not M1 startup dependencies.
