# M6 Windows packaging verification — 25 October 2026

Status: **PARTIAL**. Portable application and staging archives verified. The
team-approved final report PDF is missing, and a teammate must review the PR.
Nothing was uploaded to Microsoft Teams. No final report was generated.

## Repository and scope

- Fetched `origin`; base main is `b4a291e826b5d3d3733d270049a686647ff4549b`.
- Continued the existing `feat/windows-submission-package` branch.
- Confirmed visualization integration `94b0b58` and large-grid fix `184a755`
  are ancestors of current main.
- Preserved the unrelated untracked `README_KIT.txt`.
- No files under `src/dss` or existing tests changed. Shared API remains v0.2.

## Environment and repairs

Windows x64; Windows PowerShell **5.1.26100.9711**; existing Python **3.11.17**
environment retained; PyInstaller **6.22.3**, hooks-contrib **2026.9**;
PySide6 **6.12.0**, NumPy **2.4.6**, Matplotlib **3.11.2**.
`pip check` returned `No broken requirements found.`

The numeric Python version probe avoids embedded double quotes. Interpreter
execution failure and a genuinely wrong version now have separate errors.
Rebuilds back up prior staging and ZIP output, carrying reports/screenshots
forward instead of deleting human deliverables.

Actual frozen checks exposed and led to repairs for:

1. A QtWidgets DLL import failure. PyInstaller had collected Poppler's `icuuc.dll`
   from the development PATH. Its suffixed ICU exports do not satisfy Qt's
   Windows ICU imports. Freezing now uses only Python and Windows paths.
2. A native window with nonfunctional Run: dynamic solver imports were absent.
   `--collect-submodules dss` now includes analytical, numerical, visualization
   and UI modules.
3. PNG working while PDF export failed: Matplotlib's dynamically selected PDF
   backend was absent. It is now included explicitly alongside QtAgg and Agg.

The PyInstaller warning file was inspected, including optional/platform imports
(`pwd`, `grp`, `posix`, alternative Qt bindings), optional font codecs and NumPy
attribute entries. It is not empty. The final build had no unresolved mandatory
runtime import encountered by the acceptance cases. No optional-package warning
was treated as a reason to install every possible plotting/font dependency.
Archive inspection confirmed the three Matplotlib backends and `dss` packages;
the `pytest` package was excluded.

Reference compatibility documentation:
[PyInstaller](https://pypi.org/project/pyinstaller/) and
[Qt for Python deployment](https://doc.qt.io/qtforpython-6/deployment/deployment-pyinstaller.html).
Compatibility of the exact local combination was also measured by frozen tests.

## Tests actually run

- Full headless suite: **601 passed in 22.86s**.
- Separately selected
  `test_large_grid_keeps_worker_responsive_and_preserves_every_sample`:
  **1 passed in 6.74s**. Existing 30-second timeout retained.
- `tests/ui/native_smoke.py`: **PASS**, native Windows Light/Dark, background
  worker, real response/error graphs, metrics, sliders, presets, both sizes,
  genuine PNG/PDF exports and closure.
- Final frozen build command used `-SkipTests` after those tests had passed;
  source and existing tests were unchanged. Packaging failures were repaired and
  frozen acceptance rerun, rather than reporting failed launches as successes.
- `verify_windows_exe.ps1`: **PASS** in `dist/DynamicSystemSimulator`, a separate
  temporary copy, and the final staging `Application` directory. Each run first
  checks an ordinary native main window and normal exit, then runs opt-in
  acceptance through the same EXE. Acceptance checks window exposure, actual
  QThread results, all selected methods, plotted samples, maximum absolute error
  and RMSE against actual response differences, three cases, Auto dt, dt/2,
  repeated Run, stale-result invalidation, Light/Dark, six PNG and six PDF exports,
  and normal window closure. Export destinations alone are supplied by the
  harness; the production exporter runs.
- Separate-copy evidence: `%TEMP%/DSS-portable-0cddfecc924a4629970ec277c1e3f672/Evidence`.
  PYTHONPATH/PYTHONHOME and plotting environment overrides are cleared by the
  verifier. This copy runs with its own working directory outside the checkout.
- All six isolated exported PDFs parsed successfully with pypdf, one page each;
  all six exported PNGs decoded successfully with Pillow.
- Six genuine frozen application screenshots captured for the three cases in
  Response and Error views. Representative response/error captures were visually
  inspected for readability. This is automated native acceptance, not a claim
  of exhaustive human interaction testing on every instructor computer.
- `actionlint` **1.7.12**: Windows workflow passed; PowerShell scripts parsed;
  `git diff --check` passed before commit.

## Measured examples

All cases use a0=b0=1, end time 20 s, Auto dt=0.6283185307179586 s.
The JSON evidence includes both methods' max error and RMSE at both step sizes.

| Case (a1) | Euler max error, Auto dt | Euler max error, dt/2 | RK4 max error, Auto dt | RK4 max error, dt/2 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.4245662510 | 0.1567578553 | 0.001194005947 | 0.00006920579724 |
| 2 | 0.1364512966 | 0.05623864960 | 0.002879046389 | 0.0001287740885 |
| 3 | 0.1129094825 | 0.03662194128 | 0.01334999988 | 0.0004699120848 |

## Artifacts (local, gitignored)

- EXE: `dist/DynamicSystemSimulator/DynamicSystemSimulator.exe`, **11,317,593 bytes**.
- SHA-256: `87de1f97818fe951bbde0a8b59366234302b575a2f8a7ac09663e9d8993f1ffe`.
- Staging: `dist/CMPE443_Lab1_RaidynTeam_Windows/`.
- Application includes **452 files**, **184,638,698 bytes**, including Python
  runtime, Qt DLLs/platform plugins, NumPy/OpenBLAS, Matplotlib data and fonts.
- ZIP: `dist/CMPE443_Lab1_RaidynTeam_Windows.zip`, **81,391,376 bytes**.
  CRC check, exact inventory and SHA-256 content match passed for **543 files**.
- Genuine RAR: `dist/CMPE443_Lab1_RaidynTeam_Staging.rar`, **63,768,400 bytes**,
  created with WinRAR **7.23**. `rar t` passed; every staged file was found in its
  listing, including the complete `_internal` tree and executable.
- Six screenshots in `Screenshots/Verified-20261025-210940/`.
- Final PDF: **missing**. Only a clearly labeled missing-report text is present.
- `PACKAGED-ACCEPTANCE.json` records genuine isolated frozen measurements.
- No `.venv`, Git metadata, bytecode caches, `.env` files or unrelated kit files
  were found by folder validation. No binary outputs were staged for Git.

## Remaining human work

Supply the actual team-approved final PDF, review the PR, then recreate and check
the final RAR. The current archives are explicitly staging artifacts and are
**not ready for Teams**. The pipeline does not publish a release or upload to Teams.
