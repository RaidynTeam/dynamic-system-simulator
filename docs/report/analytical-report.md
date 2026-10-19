# Analytical Solution of the Unit Step Response

## Responsibility and objective

The analytical contribution covers the mathematical model, shared parameter
and response contracts, characteristic-root classification, and the exact
zero-state unit-step response for the three cases in the lab handout. Its
purpose is to provide a reference against which Euler and RK4 approximations
can be compared on identical time samples. Numerical integration, GUI design,
and plotting are separate team responsibilities.

The requirements source is the [Lab 1 handout](../reference/Lab1-RTS-09102026.pdf),
equations (1)-(10) on pages 1-2 and tasks 1-7 on page 5. The model is

\[
y''+a_1y'+a_0y=b_0x(t),\qquad a_1,a_0,b_0>0,
\]

with unit-step input and zero initial conditions:

\[
x(t)=1\quad(t\geq0),\qquad y(0)=0,\qquad y'(0)=0.
\]

Here y is the system output, v=y' is its rate of change, and t denotes time.
The symbols are not assigned a particular mechanical unit unless a physical
system and its units are specified. The leading coefficient of y'' is one;
arbitrary initial conditions and other input signals are outside this lab model.

## Mathematical design and derivation

For t>=0, the forcing term is constant. The solution is written as the sum of
a particular solution and a homogeneous solution:

\[
y(t)=y_p(t)+y_h(t).
\]

A constant particular solution has zero derivatives, so a0*yp=b0 and

\[
K=y_p=\frac{b_0}{a_0}.
\]

The homogeneous equation has characteristic polynomial

\[
s^2+a_1s+a_0=0,\qquad
s_{1,2}=-\frac{a_1}{2}\pm\sqrt{\frac{a_1^2}{4}-a_0}.
\]

Define D=a1²-4*a0 and sigma=a1/2. The sign of D determines the form of the
homogeneous solution. Both integration constants are fixed by y(0)=v(0)=0.
The input gain b0 changes the amplitude but does not affect the characteristic
roots or the case classification.

### Case 1: complex conjugate roots, D<0

Set omega=sqrt(a0-sigma²). The roots are -sigma ± j*omega, giving

\[
y(t)=K+e^{-\sigma t}\left(C_1\cos(\omega t)+C_2\sin(\omega t)\right).
\]

At t=0, y(0)=0 gives C1=-K. Differentiating and applying v(0)=0 gives
-sigma*C1+omega*C2=0, hence C2=-K*sigma/omega. Therefore,

\[
y(t)=K\left[1-e^{-\sigma t}\left(\cos(\omega t)
 +\frac{\sigma}{\omega}\sin(\omega t)\right)\right],
\]

\[
v(t)=\frac{b_0}{\omega}e^{-\sigma t}\sin(\omega t).
\]

These expressions reproduce handout equation (8) and its derivative. The
response may overshoot K and oscillate while its envelope decays. Such
overshoot is a property of the exact model rather than a numerical error.
The handout example a1=a0=1 belongs to this case.

### Case 2: repeated real root, D=0

The repeated root is -sigma. The homogeneous solution contains an additional
t factor because two copies of the same exponential would not be independent:

\[
y(t)=K+(C_1+C_2t)e^{-\sigma t}.
\]

The initial conditions give C1=-K and C2=-K*sigma, resulting in

\[
y(t)=K\left[1-(1+\sigma t)e^{-\sigma t}\right],
\qquad
v(t)=K\sigma^2t e^{-\sigma t}.
\]

This is handout equation (9). Since sigma²=a0 in this case, the derivative
can also be written as b0*t*exp(-sigma*t). The handout example a1=2,a0=1 is
critically damped; the response approaches K without oscillation.

### Case 3: distinct real roots, D>0

With roots s1 and s2, the general solution is

\[
y(t)=K+A e^{s_1t}+B e^{s_2t}.
\]

The initial conditions require A+B=-K and A*s1+B*s2=0. Solving these equations
and using s1*s2=a0 gives

\[
A=\frac{Ks_2}{s_1-s_2},\qquad B=\frac{Ks_1}{s_2-s_1},
\]

\[
y(t)=K\left[1+\frac{s_2}{s_1-s_2}e^{s_1t}
                  +\frac{s_1}{s_2-s_1}e^{s_2t}\right],
\]

\[
v(t)=\frac{b_0}{s_1-s_2}\left(e^{s_1t}-e^{s_2t}\right).
\]

This is handout equation (10) and its derivative. For positive a1 and a0,
both roots are negative. The handout example a1=3,a0=1 is overdamped and
approaches K without oscillation.

### Stability and limiting behaviour

For complex roots the real part is -a1/2<0. For distinct real roots,
sqrt(a1²/4-a0)<a1/2, so both roots are negative; the repeated root is also
negative. Consequently, all transient terms decay. In particular,
t*exp(-sigma*t) also tends to zero, so all three cases satisfy

\[
\lim_{t\to\infty}y(t)=\frac{b_0}{a_0},\qquad
\lim_{t\to\infty}v(t)=0.
\]

The damping ratio zeta=a1/(2*sqrt(a0)) gives the same classification:
0<zeta<1, zeta=1, and zeta>1 correspond to Cases 1, 2, and 3. These stable
physical responses can still be approximated poorly by an unsuitable numerical
step size. Physical stability and numerical stability are separate properties.

## Implementation and interfaces

The implementation evaluates the formulas with NumPy float64 arrays and does
not call a general-purpose ODE solver. The analytical module depends on the
shared contracts and NumPy, with no Qt or plotting dependency.

| Interface | Purpose |
|---|---|
| `ModelParams(a1, a0, b0)` | Stores the three positive, finite lab coefficients |
| `SimulationConfig(t0, t_end, dt)` | Stores time settings; the lab requires t0=0 |
| `classify_roots(model)` | Returns the characteristic-root class |
| `classify_case(model)` | Maps that class to handout Case 1, 2, or 3 |
| `solve_analytical(model, t)` | Evaluates both y and v at the supplied time samples |
| `Response(t, y, v, method)` | Transfers validated curves to downstream modules |

The time array must be one-dimensional float64, finite, strictly increasing,
start at zero, and contain at least two samples. Returned arrays have matching
shapes; the response owns copies so input arrays are not modified. The arrays
remain mutable even though their dataclass fields are frozen. The analytical
solver evaluates the supplied times directly; it does not march from the
previous sample or choose a time step. This makes it independent of the
numerical-method implementation.

Invalid input raises ValueError. Arithmetic overflow or non-finite calculated
results raise FloatingPointError. The implementation does not promise to
support arbitrary coefficient magnitudes when intermediate expressions exceed
the float64 range.

### Floating-point precautions

The closed-form equations are exact mathematical solutions, but computer
evaluation still involves rounding. Root classification avoids forming a1²
and 4*a0 directly. With scale=max(a1,2*sqrt(a0)), it evaluates

\[
q=(a_1/\mathrm{scale})^2-(2\sqrt{a_0}/\mathrm{scale})^2.
\]

Values satisfying |q|<=64*float64_epsilon use the repeated-root branch. This
is a documented relative floating-point convention; it does not assert that
nearby noncritical models are symbolically identical to a critical model.
The epsilon multiple is an implementation choice, not a handout requirement.

The evaluator uses expm1 to calculate exp(x)-1 accurately near zero and sinc
to evaluate sin(omega*t)/omega continuously near critical damping. In Case 3,
the slow root is calculated as -a0/(sigma+delta), where
delta=sqrt(sigma²-a0), to avoid cancellation in -sigma+delta. The two decaying
exponentials are factored instead of forming a potentially overflowing
exp(-sigma*t)*cosh(delta*t) product.

At very small times, all three responses involve cancellation between terms
close to one another. When max(a1,sqrt(a0))*t<0.01, the implementation evaluates
a degree-12 power series obtained from the same differential equation. Writing
y=sum(c_n*t^n), the coefficients satisfy

\[
c_0=c_1=0,\qquad c_2=\frac{b_0}{2},\qquad
c_n=-\frac{a_1(n-1)c_{n-1}+a_0c_{n-2}}{n(n-1)}\quad(n\geq3).
\]

The derivative is evaluated from the same series. This is a local evaluation
of the analytical model, not an Euler or RK4 integration step. The threshold
and truncation degree are numerical implementation choices checked by tests.

## Verification and measured comparison

The analytical tests use independently evaluated Decimal references at up to
80 decimal digits for the three cases, rather than deriving expected results
from Euler or RK4. Additional checks cover zero initial conditions, the steady
limit, input gain scaling, near-critical models, small times, separated root
scales, numerical derivative consistency, and the differential-equation residual.
These checks provide evidence over the tested examples, not a universal error
bound for every possible input.

M4 compared the actual analytical, Euler, and RK4 implementations at identical
time samples. The handout examples used a0=b0=1, a1=1,2,3 and an experiment end
time of 20. Starting with h0=0.1*2*pi/sqrt(a0), complete runs were repeated with
half the previous step until both numerical methods had sampled maximum output
error <=0.01. The end time and the 0.01 agreement target were team choices.

| Case | Initial Euler maximum error | Initial RK4 maximum error | First tested h satisfying both targets | Halvings |
|---|---:|---:|---:|---:|
| 1 | 4.2456625100e-1 | 1.1940059470e-3 | 0.0196349541 | 5 |
| 2 | 1.3645129660e-1 | 2.8790463888e-3 | 0.0392699082 | 4 |
| 3 | 1.1290948247e-1 | 1.3349999881e-2 | 0.0785398163 | 3 |

At the initial h0=0.6283185307, RK4 was more accurate in all three examples,
but Case 3 still exceeded the selected RK4 target. The initial step suggested
by the handout is therefore a starting value to investigate, rather than a
guarantee of agreement. Errors were measured at samples; the comparison does
not establish an upper error bound over the continuous interval.

A separate Case 2 endpoint experiment at t=2 used h=0.1,0.05,0.025. Successive
Euler error ratios were 2.054061 and 2.025975; RK4 ratios were 17.023675 and
16.505859. They approach the expected factors 2 and 16 for first- and
fourth-order global convergence in this regime. These are the same M4
measurements used in the numerical report contribution and should be included
only once when assembling the common report.

## Conclusion

The analytical contribution provides the required three zero-state unit-step
responses and their derivatives behind one validated interface. Characteristic
roots explain the oscillatory or nonoscillatory behaviour and the common limit
b0/a0. Independent high-precision checks and the measured numerical comparisons
support the implementation over the tested conditions. The formulas also
provide a reference for judging how Euler and RK4 improve when their step size
is reduced. Final application screenshots and the complete team report are
separate integration deliverables.

## Sources and reproducibility

- [Lab 1 handout](../reference/Lab1-RTS-09102026.pdf), equations (1)-(10), pages 1-2;
  tasks 1-7, page 5.
- [Analytical source](../../src/dss/analytical/solver.py) and
  [classification](../../src/dss/analytical/classification.py).
- [Analytical tests](../../tests/analytical/), including the independent references.
- [M4 measured comparison](../evidence/analytical-m4-verification.txt), recorded
  on Python 3.11.17/macOS with NumPy 2.4.6 and pytest 9.1.1.
- Reproduce tests with `QT_QPA_PLATFORM=offscreen MPLBACKEND=Agg python -m pytest -q`;
  reproduce the comparison with `PYTHONPATH=src python tests/numerical/experiments.py`.
