# Dynamic System Simulator — Windows submission

**Course:** CMPE 443 / CMSE 443, Lab 1

**Team:** RaidynTeam

**Platform:** Windows 10/11, 64-bit

## How to run the program (no Python installation required)

1. Extract the **entire** submission archive to a local directory. Do not run the EXE from inside an archive.
2. Open `Application`.
3. Double-click **`DynamicSystemSimulator.exe`**.
4. Select Case 1, 2 or 3. Leave Exact, Euler and RK4 selected and click **Run Simulation**.
5. The Response graph compares the methods. Choose **Error** to inspect differences, and **PNG/PDF** to save a figure.

**Important:** `Application/_internal` contains the Python runtime, Qt plugins and scientific dependencies. Keep it beside the EXE. Do not send `DynamicSystemSimulator.exe` on its own.

The portable build is produced on Windows with Python 3.11 and PyInstaller. It bundles its Python dependencies; there is no installer. A Windows security notification may appear for an unsigned academic application: confirm its provenance with the team before running it. No administrator access should be required for the normal app.

## Submission contents

- `Application/` — portable EXE plus all required runtime files.
- `Source-Code/` — Python source code, tests and project dependencies, for review/reproduction.
- `Final-Report/` — **team must insert the approved final PDF**; a placeholder is not a report.
- `Screenshots/` — six genuine application captures from packaged acceptance (Response and Error for each case). Rebuilds retain existing captures and add a timestamped set.
- `START_HERE.md` — these instructions.

## Teacher / team verification

Case 1 uses a1=1, a0=1; Case 2 uses a1=2, a0=1; Case 3 uses a1=3, a0=1. Set b0=1 for the laboratory comparisons. Exact is the analytical reference, Euler is a first-order approximation, and RK4 is a fourth-order approximation. Response shows the computed output; Error shows absolute differences from Exact. Maximum absolute error and RMSE summarize those differences. Error curves and RMSE require Exact together with a numerical solver. Auto dt supplies the lab's initial time step; dt/2 halves it and requires a new Run. Changing inputs clears stale results. The theme button switches Light/Dark. PNG and PDF save the currently selected Response or Error figure.

The build checks a normal native window and normal closure, then exercises all three cases inside the frozen executable using the production UI, worker and exporters. It compares plotted samples and displayed error metrics with the actual responses, tests repeated Run, Auto dt, dt/2, stale-result invalidation, both themes and PNG/PDF export. It repeats acceptance in a temporary directory outside the source checkout with Python import environment variables cleared. `PACKAGED-ACCEPTANCE.json` records measured results. This is automated native acceptance; it does not claim a human has reviewed every UI interaction.

## Rebuilding and preserving deliverables

Run `powershell -NoProfile -ExecutionPolicy Bypass -File tools/build_windows_submission.ps1`
from the repository on Windows with Python 3.11. A valid existing `.venv` is reused.
Dependencies are pinned by `requirements.lock.txt`; the build uses PyInstaller
6.22.3 and its installed hooks. Development modules such as pytest are excluded
from the frozen application. Source, test and build tools remain available under
`Source-Code`. The source dependency lock also includes test dependencies; that
does not mean those packages are included in the EXE.

The build explicitly collects all `dss` modules because the UI imports solvers
and visualization at execution time. It includes Matplotlib's QtAgg, Agg and PDF
backends. During freezing, PATH is limited to the selected Python environment
and Windows system directories so unrelated toolchain DLLs cannot enter the
bundle. `-SkipTests` and `-SkipBuild` are local incremental-work options; the
default command and CI always run tests and create a fresh EXE. Only reuse a
build when the application and frozen acceptance sources are unchanged.

When rebuilding, the previous staging folder is moved to a timestamped backup
under `dist`, and its `Final-Report` and `Screenshots` contents are copied forward.
Existing ZIP files are also backed up. Do not delete those backups until their
contents have been checked. No report is selected automatically from unrelated
PDF files or drafts. A missing final report is reported explicitly.

GitHub Actions provides the same build through **Windows portable submission
build**. Download **CMPE443-Lab1-Windows-portable** from a successful run's
Artifacts section. CI produces a staging ZIP, not a release or a final RAR.

To create and check a genuine RAR locally, run
`powershell -NoProfile -File tools/create_submission_rar.ps1 -PackagePath dist/CMPE443_Lab1_RaidynTeam_Windows`.
It uses WinRAR's `rar.exe`, tests archive integrity and checks that every staged
file is listed, including all of `_internal`. If the approved PDF is missing,
the archive is named `CMPE443_Lab1_RaidynTeam_Staging.rar` and is explicitly
incomplete. Only place an approved final PDF in `Final-Report`; the tool cannot
establish team approval merely from a PDF's existence.

**Before sending:** The instructor's handout requires a **RAR submission archive**, source files, the executable program and report, plus a printed copy of the report. The automatically generated ZIP is a *staging artifact*, not an assertion that the final submission is complete. After adding the final report and genuine screenshots, use WinRAR/compatible software to create `CMPE443_Lab1_RaidynTeam_Final.rar` from the top-level submission folder and upload that RAR through Teams. Do not upload only the EXE or a folder missing its `_internal` subdirectory.
