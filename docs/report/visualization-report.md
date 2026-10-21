# Visualization, Error Metrics and Export

## Responsibility and objective

This part of the project turns the three computed responses into something a
reader can judge. It owns `src/dss/visualization/`, `src/dss/demo_data.py`,
`tests/visualization/` and `CONTRIBUTING.md`.

The handout asks for comparative graphs of the analytical, Euler and RK4
responses for all three cases, and for the comparison to be repeated with a
halved step when the numerical and analytical results disagree. Deciding
whether they agree needs two things the handout does not supply: a figure in
which the three curves can actually be told apart, and a number that says how
far apart they are. Those two are the objective here.

Four functions are delivered, with the signatures fixed in the shared v0.2
contract:

```python
compute_error(reference, candidate) -> ErrorMetrics
build_response_figure(responses) -> Figure
build_error_figure(reference, candidates) -> Figure
export_figure(figure, path) -> None
```

The solvers themselves are not implemented here. The analytical reference is
Person 1's `solve_analytical`, the numerical candidates are Person 2's
`solve_euler` and `solve_rk4`, and the shared time grid comes from Person 2's
`make_time_grid`. The Qt window and canvas placement belong to Person 3.

## Design

### Figures without pyplot

Figures are built from `matplotlib.figure.Figure` directly. `matplotlib.pyplot`
is never imported. That is a deliberate constraint rather than a style
preference: pyplot keeps every figure in a global manager, so a long session
accumulates figures that are only released by an explicit `close`, and
importing it selects a GUI backend at import time. Inside a PySide6 application
that backend selection collides with the one Qt already owns.

Building the `Figure` object directly avoids both. No figure is registered
anywhere, nothing has to be closed, and no backend is chosen until something
actually draws. Person 3 attaches the returned figure to a
`FigureCanvasQTAgg`; export attaches an Agg canvas; a test attaches neither and
still gets a valid figure. A subprocess test asserts that after building a
figure, neither `matplotlib.pyplot` nor any Qt package has reached
`sys.modules`.

Every call returns a new figure, so a repeated run cannot draw onto the
previous one.

### Telling the three curves apart

The team agreed on three identity colours: Exact `#475569`, Euler `#FF1D8D`,
RK4 `#2563EB`. Colour alone is not enough, for two reasons. Readers with a
colour vision deficiency lose the distinction, and a printed report may be
greyscale. Each method therefore also carries its own dash pattern, line width
and marker.

The reference curve is drawn widest and lowest in the stacking order. This came
out of looking at a real render rather than from theory: RK4 tracks the exact
response so closely that at equal line widths it covers it completely. With the
reference wider, a grey halo stays visible on both sides of the overlaying
dashed curve, and the two can be distinguished at a glance.

Markers are thinned to at most forty per curve. At the smallest step used in
the experiments the grid holds 1020 samples; a marker per sample paints a solid
band and hides the curve it was meant to annotate.

The y axis carries no physical unit. The handout never states what y measures,
so a unit would be an assertion the assignment does not support. The axis is
labelled `Output y(t)` and the time axis `Time (s)`, seconds being the unit the
project's own examples use.

### What the error metric measures, and what it refuses to

The shared contract fixes both formulas and restricts them to position:

```
max_abs = max(|candidate.y - reference.y|)
rmse    = sqrt(mean((candidate.y - reference.y)^2))
```

The two answer different questions. `max_abs` is the worst single sample, which
is what matters when a single visible deviation would be unacceptable. `rmse`
is the typical deviation across the whole interval, which is what matters when
the overall agreement is the question. For Case 1 at the initial step the Euler
figures are 4.2456625100e-01 and 1.5404233297e-01: the worst sample is about
2.8 times the typical one, because Euler's error concentrates around the
overshoot and decays afterwards. Reporting only one of the two would hide that.

Three things are deliberately excluded.

**The velocity error is not folded in.** A single number mixing a position and
a velocity error describes neither, and the handout compares the step response
y(t).

**No percentage error.** The response starts at y(0) = 0, so a relative error
divides by zero at the first sample and is dominated by noise near it.

**No interpolation.** Both responses must carry exactly the same time samples,
checked with `np.array_equal`. Comparing different grids would require
inventing values that neither solver produced, so a mismatch raises instead of
being silently resampled.

One deviation from the literal formula is worth recording. Computing
`mean(d**2)` directly overflows float64 once `d` passes roughly 1e154. The
implementation factors the largest deviation out before squaring, which returns
the same value without that ceiling. A test demonstrates the naive form
returning `inf` where this one stays finite.

## Implementation and interfaces

| Module | Contents |
|---|---|
| `visualization/styles.py` | Method identity and theme palettes; imports neither Matplotlib nor Qt |
| `visualization/figures.py` | Qt-free figure factory, axes styling, theme re-application |
| `visualization/plots.py` | `build_response_figure`, `build_error_figure` |
| `visualization/metrics.py` | `compute_error`, `error_signal` |
| `visualization/export.py` | `export_figure` |
| `demo_data.py` | Deterministic development fixtures, not imported by the application |

Person 3 reaches these through `dss.ui.presentation`, which loads the four
contract functions lazily and refuses to display anything unless all four exist
and return the shared types.

Two signatures were extended with keyword-only parameters that carry defaults,
so the contract's positional calls are unchanged:
`build_response_figure(responses, *, theme, title)`,
`build_error_figure(reference, candidates, *, theme, title, scale)` and
`export_figure(figure, path, *, dpi)`.

Export deserves one note. The UI may ask to export a figure that is at that
moment displayed on a `FigureCanvasQTAgg`. `figure.savefig` switches to the
backend the file extension requires and restores `figure.canvas` afterwards, so
the figure is not detached from its widget. This was verified experimentally
before being relied upon, and a test now holds it in place. Export creates no
directory, preserves the theme background rather than writing a dark figure
onto a white page, and removes a file it created but could not finish, so a
failed export cannot leave an empty stub behind.

## Experiments and results

All measurements below come from running the real solvers through the real
metric. The full record, including every intermediate step and the environment
versions, is in `docs/evidence/visualization-m4-experiments.md` and is
reproduced by `python tests/visualization/error_experiments.py`.

Common parameters: a0 = 1, b0 = 1, t0 = 0, t_end = 20 s. The initial step is the
handout's T = 0.1 * 2 * pi / sqrt(a0) = 0.6283185307 s, halved five times.

### At the initial step

| Case | a1 | Method | max abs error | RMSE |
|---|---:|---|---:|---:|
| 1 | 1 | Euler | 4.2456625100e-01 | 1.5404233297e-01 |
| 1 | 1 | RK4 | 1.1940059470e-03 | 4.0023800218e-04 |
| 2 | 2 | Euler | 1.3645129660e-01 | 4.8294113609e-02 |
| 2 | 2 | RK4 | 2.8790463888e-03 | 7.5469918013e-04 |
| 3 | 3 | Euler | 1.1290948247e-01 | 3.7520057063e-02 |
| 3 | 3 | RK4 | 1.3349999881e-02 | 2.5920087393e-03 |

At this step Euler is visibly wrong in Case 1: the response overshoots to 1.565
where the exact peak is 1.162, and the oscillation persists well past the
point where the exact response has settled. The handout's instruction to halve
the step until the results agree has a clear starting point here.

### After five halvings

| Case | Method | max abs error | RMSE | previous/this |
|---|---|---:|---:|---:|
| 1 | Euler | 7.7908424168e-03 | 2.4877967479e-03 | 2.03 |
| 1 | RK4 | 9.7515684416e-10 | 3.1147582105e-10 | 16.09 |
| 2 | Euler | 3.0583029078e-03 | 1.1041537133e-03 | 2.02 |
| 2 | RK4 | 1.4572643092e-09 | 3.7435414690e-10 | 16.34 |
| 3 | Euler | 1.5964778004e-03 | 7.6431437123e-04 | 2.01 |
| 3 | RK4 | 3.8119149573e-09 | 7.1476661629e-10 | 16.70 |

The last column is the previous level's error divided by this level's. Halving
the step divides the Euler error by about 2 and the RK4 error by about 16,
across all three cases. Those are 2^1 and 2^4: the observed orders match a
first-order and a fourth-order method. The ratios were measured, not derived,
and they converge towards the theoretical values as the step shrinks and the
higher-order terms stop contributing.

The practical reading: at the initial step RK4 is already about 350 times more
accurate than Euler in Case 1, and each halving widens the gap by a further
factor of eight.

### Independent cross-check

Person 2 measured the maximum errors for six of these configurations with their
own script, recorded in `docs/modules/numerical-handoff.md`. Those measurements
and the ones produced here by `compute_error` agree to every digit printed, for
all six. Two people, two independent code paths, the same numbers. That is the
strongest available evidence that the metric is implemented correctly, and it
is stronger than the hand-computed unit test, which only covers three samples.

### Reading the error figure

On a linear axis RK4's error sits on zero next to Euler's and cannot be
assessed. The error figure therefore offers a logarithmic axis, where the three
to five orders of magnitude between the two methods become visible. A log axis
cannot place a non-positive value, and the first sample is always exactly zero
because every solver starts from the same y(0) = 0; those samples are masked, so
the curve is interrupted rather than being given a substituted floor value.

## Conclusion

The comparison the handout asks for is now reproducible end to end: the same
time grid feeds all three solvers, the figure separates them by colour, dash
pattern, width and marker, and the metric quantifies the gap without
interpolating or inventing a unit.

The measurements confirm what the methods' orders predict. Euler's error falls
linearly with the step and RK4's falls with the fourth power, so a step that is
adequate for RK4 can still leave Euler visibly wrong, as Case 1 at the initial
step shows. Choosing a step by looking at Euler alone would therefore be
overly conservative for RK4, and choosing it by looking at RK4 alone would be
wrong for Euler.

What this work does not establish: the figures and the metric are verified, but
the accuracy of the underlying solvers is Person 1's and Person 2's to defend,
and the application's end-to-end behaviour on a real desktop is Person 3's.

## Sources and reproducibility

- Handout: `docs/reference/Lab1-RTS-09102026.pdf`; requirement mapping in
  `docs/lab-requirements.md`
- Team contributions used here: Person 1's `solve_analytical` and the shared
  `contracts.py`; Person 2's `make_time_grid`, `solve_euler`, `solve_rk4` and
  the independent measurements in `docs/modules/numerical-handoff.md`;
  Person 3's `ui/presentation.py` boundary and the agreed method colours
- Module notes and verification record: `docs/modules/visualization.md`
- Test and measurement records: `docs/evidence/visualization-m1-*`,
  `-m2-tests.txt`, `-m3-tests.txt`, `-m4-tests.txt`, `-m4-experiments.md`
- Reproduce the measurements: `python tests/visualization/error_experiments.py`
- Reproduce the figures: `python tests/visualization/preview.py --format both`
- Full test suite: `QT_QPA_PLATFORM=offscreen MPLBACKEND=Agg python -m pytest -q`
