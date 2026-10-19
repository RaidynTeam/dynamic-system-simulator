# Numerical Solution of the Unit Step Response

## Responsibility and objective

The numerical-methods contribution covers the shared time grid, the forward
Euler solver, the fourth-order Runge-Kutta solver, numerical tests, and the
Windows test workflow. The objective is to approximate the system output and
compare the numerical results with the analytical solutions for the three cases
in the lab handout. Analytical solution development, the user interface, and
graph plotting are separate team responsibilities.

The mathematical requirements come from **Lab1 RTS 09102026.doc**. The model is

\[
y''+a_1y'+a_0y=b_0x(t),\qquad y(0)=y'(0)=0,
\]

where the coefficients are positive and the input is a unit step. Therefore,
for the simulated interval t>=0, x(t)=1.

## Algorithm and design

Introducing v=y' changes the second-order equation into two first-order
equations, as in handout equation (12):

\[
y'=v,\qquad v'=b_0-a_1v-a_0y.
\]

Both numerical methods use the state s=[y,v] and the same derivative function
f(s)=[v,b0-a1*v-a0*y]. This keeps the physical model identical in both solvers.

### Time grid

The time grid begins at zero and includes the requested end time. Full steps
are calculated by multiplying the step size by an integer index. If the end
time is not a multiple of the step size, only the final interval is shortened.
For example, an end time of 1 and a step of 0.3 produce
[0, 0.3, 0.6, 0.9, 1]. Each solver uses h=t[i+1]-t[i], so it also handles this
short final interval correctly. All compared methods receive identical time
samples.

### Forward Euler

Handout equation (15) gives the following updates:

\[
y_{i+1}=y_i+h v_i,
\qquad
v_{i+1}=v_i+h(b_0-a_1v_i-a_0y_i).
\]

Both updates use the old state. The implementation calculates the complete
next state before storing it. Using the updated output in the velocity update
would change the method. For a1=2, a0=b0=1 and h=0.1, the first two states after
the initial state are (y,v)=(0,0.1) and (0.01,0.18).

### Fourth-order Runge-Kutta

Handout equations (18)-(19) evaluate four intermediate stages:

```text
k1 = f(s)
k2 = f(s + h*k1/2)
k3 = f(s + h*k2/2)
k4 = f(s + h*k3)
s_next = s + h*(k1 + 2*k2 + 2*k3 + k4)/6
```

Each stage advances both state components together. The k values in the code
are slopes; the increment terms in the handout equal h*k. Thus, h is included
once in the final weighted update. Euler uses one derivative evaluation per
step, while RK4 uses four.

## Implementation and interfaces

The implementation uses Python and NumPy. No general-purpose ODE solver is
called. The numerical module has no dependency on the GUI or plotting library.

| Function | Input | Output and purpose |
|---|---|---|
| `make_time_grid(config)` | Start time, end time, step size | A float64 NumPy time array |
| `solve_euler(model, t)` | a1, a0, b0 and time samples | Euler response with t, y, v and method name |
| `solve_rk4(model, t)` | The same model and time samples | RK4 response with t, y, v and method name |

Each response starts with y=v=0. Input arrays are not modified, and the returned
response owns copies of its arrays. Invalid parameters or time samples produce
a clear input error. Arithmetic overflow produces a calculation error instead
of an invalid response. Neither solver silently changes the supplied time grid.

The one-million-sample limit is an implementation choice to bound memory use.
It is not a requirement stated in the handout.

## Experiments and results

### Step halving for the three cases

Following tasks 5-7 in the handout, the initial step was

\[
h_0=0.1\frac{2\pi}{\sqrt{a_0}}.
\]

The handout examples use (a1,a0)=(1,1), (2,1), and (3,1). We selected b0=1 and
an end time of 20 for these experiments. The handout does not specify a numerical
agreement tolerance. For these unit-gain examples, we selected a maximum
absolute output error of 0.01 for both methods:

\[
E_{\max}=\max_i\left|y_{\mathrm{numerical}}(t_i)-y_{\mathrm{analytical}}(t_i)\right|.
\]

The analytical solutions were evaluated on exactly the same grid as the
numerical solutions. The step was halved and the full simulation repeated until
both methods met the selected target. The following are measured results.

| Case | a1 | Initial h | Initial Euler max error | Initial RK4 max error |
|---|---:|---:|---:|---:|
| 1 | 1 | 0.6283185307 | 4.2456625100e-1 | 1.1940059470e-3 |
| 2 | 2 | 0.6283185307 | 1.3645129660e-1 | 2.8790463888e-3 |
| 3 | 3 | 0.6283185307 | 1.1290948247e-1 | 1.3349999881e-2 |

| Case | Halvings | Final h | Samples | Final Euler max error | Final RK4 max error |
|---|---:|---:|---:|---:|---:|
| 1 | 5 | 0.0196349541 | 1020 | 7.7908424168e-3 | 9.7515684416e-10 |
| 2 | 4 | 0.0392699082 | 511 | 6.1668402676e-3 | 2.3812393501e-8 |
| 3 | 3 | 0.0785398163 | 256 | 6.4584911355e-3 | 1.1100609671e-6 |

RK4 was more accurate than Euler at the same initial step in all three
examples. However, its initial error in Case 3 also exceeded 0.01. Therefore,
using RK4 does not remove the need to select a suitable step size. The reported
maximum errors apply to the sampled points, rather than to every point in
continuous time. Step values in the tables are rounded for display; the
experiment uses the full floating-point values.

### Additional convergence check

A separate test used a1=2, a0=b0=1 and the analytical result from handout
equation (9), y(t)=1-(1+t)exp(-t). The endpoint was chosen as t=2. The table
reports the absolute error at this endpoint and the ratio E(h)/E(h/2).

| Method | h | Endpoint error | Previous error divided by current error |
|---|---:|---:|---:|
| Euler | 0.1 | 1.4258851585e-2 | - |
| Euler | 0.05 | 6.9417845866e-3 | 2.054061 |
| Euler | 0.025 | 3.4263922472e-3 | 2.025975 |
| RK4 | 0.1 | 5.1085177122e-7 | - |
| RK4 | 0.05 | 3.0008312391e-8 | 17.023675 |
| RK4 | 0.025 | 1.8180400518e-9 | 16.505859 |

The ratios approach 2 for Euler and 16 for RK4. This is consistent with global
errors of order h and h^4 for smooth solutions in the convergence regime. The
endpoint is intentionally not t=1: in this particular example, the leading
Euler output-error term vanishes at t=1 and would give a misleading order
estimate from that point alone. This convergence test is an additional
verification choice, not a separate requirement in the handout.

### Stability and verification

A stable physical model can have an unstable numerical approximation. For
u'=lambda*u, Euler multiplies the previous value by 1+h*lambda. Decay therefore
requires |1+h*lambda|<1. For the repeated root lambda=-1, this requires 0<h<2.
A test with h=3 confirms that Euler can produce growing values even though the
physical response approaches 1. The solver reports these finite values without
silently reducing h; arithmetic overflow is reported explicitly.

The numerical module has 58 passing tests. They cover hand-calculated steps,
independent analytical reference values for all three cases, initial
conditions, shortened and irregular intervals, input ownership, invalid inputs,
overflow, and convergence. A recorded full-project run passed 220 tests on
Windows with Python 3.14.5. The Windows/Python 3.11 GitHub Actions run also
passed for merged commit `2b51883`.

## Conclusion

Both methods approximate the required zero-state unit-step response and return
compatible results on a shared time grid. Euler is simple and uses fewer
derivative evaluations per step, but it required smaller steps to reach the
selected accuracy target in these experiments. RK4 produced substantially
smaller errors at the same step sizes. Repeated step halving achieved the chosen
agreement target for all three examples. The measurements support the expected
convergence behaviour and show why step size and numerical stability must be
checked rather than assumed.

## Sources and reproducibility

- **Lab1 RTS 09102026.doc**, equations (1)-(4), (12), (15), (18)-(19), analytical
  reference equations (8)-(10), and tasks 5-7.
- [Complete experiment output](../evidence/numerical-experiments.md), including
  every halving and the Python/NumPy versions.
- [Recorded full-project test output](../evidence/numerical-tests.txt).
- [Windows and Python 3.11 CI result](https://github.com/RaidynTeam/dynamic-system-simulator/actions/runs/39309145462).
- Reproduce from the installed project with `python -m pytest -q` and
  `python tests/numerical/experiments.py`.
