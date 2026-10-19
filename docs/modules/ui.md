# UI — Person 3, M2

## Current milestone: M2 slider controls

M1 was confirmed merged in `origin/main` at `bb9a9d7`. The working tree was
clean, remote deletion of feat/ui-m1 was confirmed, main was updated using
`git pull --ff-only origin main`, and a fresh `feat/ui-m2` was created from it.
The old M1 branch was not reused. Current AGENTS.md, API v0.2, role guide,
source, tests, README and this handoff were read before edits. The PDF's relevant
model/case/task text on pages 1, 2 and 5 was re-read for M2.

### Controls and state flow

`ui/slider_input.py` adapts an integer QSlider to a float value and a read-only
numeric QLabel. It emits valueChanged or valueRejected; invalid requests keep
the previous value and report why. Widgets, immutable LabInputs, controller and
the existing Matplotlib placeholder retain the M1 dependency structure.

| Input | Slider mapping | UI range |
|---|---|---|
| a1, a0, b0 | value = integer / 100 | 0.01–20.00, step 0.01 |
| dt | value = 10 ** (-6 + integer / 200) | 1e-6–10 s, integers 0–1400 |

These ranges are UI choices, not academic coefficient bounds. Range labels and
tooltips make them visible. Off-grid coefficient setter requests are rejected,
not rounded. The label shows coefficients to two decimals and dt to 12
significant digits. Auto dt and dt / 2 or dt × 2 retain the full float value,
including values between log ticks; only the thumb position is rounded. Actual
slider movement selects the corresponding log tick value. This avoids cumulative
rounding during repeated halving. No coefficient or dt keyboard text box remains;
standard slider arrow keys are supported for accessibility.

Auto dt starts enabled: dt = 0.1 * 2*pi/sqrt(a0). Changing a0 recomputes dt only
while enabled. Manual dt changes, including successful halve/double operations,
disable Auto. Re-enabling Auto, selecting a Case, or Reset restores the formula.
Case 1/2/3 set a1 to 1/2/3 and a0 to 1, preserve b0, and synchronize readouts and
thumbs without recursive signals. Editing a1/a0 selects Custom. A rejected
halve/double request displays an error and keeps the previous dt and Auto mode.

Start/end times have separate QLineEdit controls. Start is read-only at zero
because the instructor's initial conditions and API v0.2 require t0=0. End time
accepts dot-decimal/scientific notation; commas are rejected with an example.
Invalid text stays visible rather than being coerced to a default. The UI checks
finite positive values, t0=0, methods and estimated sample count
`ceil((t_end-t0)/dt)+1 <= 1_000_000`. Oversized or overflowing estimates report a
configuration error. This preflight allocates no grid; numerical code remains
responsible for its own final grid validation. Valid subsequent edits clear the
error. Run remains a skeleton action; it never calls real solvers or displays
fake results. The existing M1_STATUS constant name is retained for compatibility,
but its displayed text now says UI skeleton.

API v0.2 field adapters are unchanged except that config_kwargs reads explicit
LabInputs.t0. The legacy general model mapping is retained. No edits to shared
contracts, numerical, analytical, visualization, dependencies or CI were made.

### M2 verification and handoff

- Contract: ORTAK-SOZLESME-v0.2; branch: `feat/ui-m2`; commits: see Git/PR history.
- Implementation: M2 complete; M3 not started. Next action is team review.
- Full `.venv/Scripts/python.exe -m pytest -q`: **137 passed**. Existing M1
  behavior remains covered alongside analytical and shared-contract tests.
- New tests cover integer/float/readout synchronization, all three presets,
  log mapping, exact initial dt, Auto, manual override, restoration, 15 repeated
  halvings and inverse doublings, coefficient/dt boundaries and rejection,
  invalid time text, NaN/Inf, overflowing estimates, sample budget and recovery.
- An intermittent startup-subprocess access violation was found during reruns.
  Self-capturing button lambdas were replaced with bound Qt slots so closed
  windows can be released before interpreter shutdown. A weak-reference lifecycle
  regression test checks this. The startup test now stops/disconnects its owned
  timers and enables subprocess faulthandler diagnostics; three consecutive
  isolated startup runs and the final full suite passed after the fix.
- `.venv/Scripts/python.exe tests/ui/native_smoke.py`: **PASS** on native Windows,
  using a real Qt event loop and QTest slider key input. Checks sliders, presets,
  Auto, halving, invalid input, Run, minimum layout and close. Default/minimum
  rendered images were visually inspected; local evidence is ignored under
  `.venv/ui-m2-native*.png`. Run stays visible and the input panel scrolls.
- `git diff --check`: passed. Runtime: Python 3.11.17, PySide6 6.12.0,
  Matplotlib 3.11.2, pytest 9.1.1. No human desktop acceptance is claimed.
- Risks: finite slider ranges deliberately restrict the UI parameter space;
  small windows require scrolling. Native Windows text is readable; the
  Windows offscreen plugin's font limitation noted in M1 remains.
- Dependencies: analytical Case 2 is now in main; other solvers and visualization
  integration remain external work. None are needed for this input milestone.
- Stop after M2; start M3 only on explicit user approval.

## Historical M1 record (superseded where M2 differs)

## Scope and source

M1 provides a PySide6 window and event loop, not simulation integration.
The instructor's **Lab1 RTS 09102026** handout was absent at initial inspection
but arrived in upstream analytical PR #1 while M1 was being implemented.
The source is now `docs/reference/Lab1-RTS-09102026.pdf`; its model/case/task
text on pages 1, 2 and 5 was inspected. The UI uses the verified requirements:
unit step, zero initial conditions, positive a1/a0/b0, Cases (1,1), (2,1),
(3,1), and initial dt = 0.1 * 2*pi/sqrt(a0). The upstream lab-requirements
mapping and shared contract are owned by Person 1 and were preserved during
merge. Full numerical comparisons and step halving remain beyond M1.

## Architecture

- `dss.__main__.main`: owns QApplication, shows MainWindow, returns event-loop exit code.
- `ui/main_window.py`: widgets, case controls, input snapshot, status presentation,
  and a single FigureCanvasQTAgg containing placeholder text. No computed curves.
- `ui/state.py`: immutable LabInputs form snapshot with no Qt dependency.
  It represents the restricted lab form, not a duplicate shared contract.
- `ui/controller.py`: retains the agreed run_simulation signature, using type-only
  imports. It explicitly raises NotImplementedError in M1. The form does not
  call it with fabricated contract objects. No shared module is imported at startup.

Upstream main now supplies API v0.2, `ModelParams(a1,a0,b0)`. Future integration
can construct `ModelParams(**inputs.lab_model_kwargs())` and
`SimulationConfig(**inputs.config_kwargs())`; an integration test constructs
these actual shared types. This does not connect the Run button to solvers.
The original task's general v0.1 fields are preserved separately by
`model_kwargs()` for compatibility; do not pass those legacy kwargs to v0.2:

| Lab form | General API v0.1 |
|---|---|
| a1, a0 | a1, a0 |
| b0 | u0 |
| Fixed normalization | a2 = 1 |
| Fixed initial conditions | y0 = 0, v0 = 0, t0 = 0 |
| End time, dt | t_end, dt |
| Exact / Euler / RK4 | analytical / euler / rk4 |

The UI makes no shared API change. The v0.2 migration came from the analytical
owner's merged PR, not a UI edit. Positive lab input bounds are UI constraints;
the original general mapping remains available without redefining shared types.
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

- Shared contract: upstream ORTAK-SOZLESME-v0.2; original v0.1 general field
  mapping preserved in UI state. No UI edits to shared contract files.
- Branch: `feat/ui-m1`; commit identifiers are available in Git history and the PR.
- Implemented milestone: M1 UI skeleton only; M2 is not started.
- Tests and actual results (2026-10-19): editable package install succeeded in
  local Python 3.11.17; PySide6 6.12.0, Matplotlib 3.11.2, pytest 9.1.1.
  Initial `python -m pytest -q`: 10 passed before upstream merge. Covers open/close, required controls,
  presets/API mapping, initial dt/refinement, empty methods/status, minimum size,
  unavailable controller, and isolated real entry point with all unfinished
  shared module imports explicitly blocked. Combined post-merge
  `python -m pytest -q`: **81 passed** (70 upstream analytical tests plus
  11 UI/integration tests, including the new actual v0.2 contract mapping).
  `git diff --check` passed.
- Automated native Windows smoke: startup, Case 3, Run status and close passed.
  Native renders at 1120x800 and 940x700 logical pixels inspected visually.
  The input pane scrolls at minimum size; Run stays visible below it.
  Offscreen Windows Qt exposes no fonts on this machine, so its pixel renders
  show missing glyphs; native Windows uses Segoe UI and renders readable text.
  Screenshots are local ignored verification artifacts under `.venv/`.
- Desktop/manual record: no human interactive desktop acceptance test performed.
  Headless lifecycle checks do not replace human desktop review.
- Next task: team review of M1. Begin M2 only with user approval.
- Integration dependencies: Person 1 analytical solver; Person 2 shared time
  grid and numerical solvers; Person 4 Figure/metrics functions. Shared contract
  types and validators are now available. None are M1 startup dependencies.
