# Contribution Guidelines

This document summarizes the Git and pull request practices agreed upon by the
team. It describes the contribution process for this repository.

**These practices are not currently enforced by GitHub.** The repository's
branch ruleset is disabled, so following this process relies on the team.

## Before You Start

`AGENTS.md` and the public API in `src/dss/contracts.py` are authoritative.
Setup and launch instructions are in `README.md`.

## Branches

- `main` is the release-ready branch. **Do not push directly to `main`.**
- Create a small branch from the latest `main` for each milestone, for example
  `feat/<scope>-m1` or `feat/<scope>-m2`.
- After a branch is merged, create the next one from the **latest `main`**. A
  single long-lived branch is not required.
- **Do not force-push.** If it is necessary (for example, to correct an author
  identity), tell the team first. Do it only on your own branch with
  `--force-with-lease`, and explain why in the pull request description.
- Do not delete another person's branch or work.

## Commits

Format: `<type>(<scope>): <English imperative description>`

Example: `feat(numerical): implement euler integration`

| | |
|---|---|
| **Types** | `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `ci` |
| **Scopes** | `analytical`, `contracts`, `numerical`, `ui`, `plot`, `analysis`, `project` |

- Each commit represents **one logical change**. Code and its tests may be
  committed together; unrelated fixes belong in separate commits.
- Write commit descriptions in English using the imperative mood.
- Do not use a type outside the list above.

**Never commit:**

- `.venv/`, `__pycache__/`, or build artifacts (all are listed in `.gitignore`).
- `.env` files, access keys, tokens, or passwords.
- Fabricated test output or unmeasured experimental results.
- Author information belonging to another person.

## Pull Requests

Include the following in every pull request description:

1. **Purpose and result** — the problem and the behavior after the change.
2. **Changes** — which files changed and what each change does.
3. **Tests and actual results** — the commands run and their **actual output**.
4. **Limitations / API impact** — whether the shared contract changed.
5. **Related task** — include the milestone. If there is no Issue number, **do
   not invent one**; use the task title instead.

Never say a test passed if it was not run. If a test could not be run, state
that clearly.

Pull request descriptions use Markdown. When copying one from a file, copy from
the **raw source**; copying from its rendered preview can lose headings and
tables.

## Reviews

The default review rotation is shown below; each arrow points from the reviewer
to the pull request author:

```
Person 1 → Person 2 → Person 4 → Person 3 → Person 1
```

- Merge through a pull request after **at least one other team member reviews**
  it.
- Do not merge until the checks pass.
- If the assigned reviewer is unavailable, **another team member may review**.
  The requirement is one review by another person; the rotation is only the
  default assignment. Record the reason for any change in the pull request.
- Submit approvals through GitHub's **Review** feature. Verbal approval is not
  recorded and cannot be included in the project report.
- All four team members review pull requests that change the shared contract.

**For reviewers:** Do not check only whether tests pass. Verify that reported
numbers were actually measured, the shared API remains compatible, and the
change does not alter files owned by another contributor without agreement.

## Shared Contract and File Ownership

- Every shared file has one owner. Do not silently change another person's
  module. Explain the need and proposed interface to its owner, then implement
  the change after agreement.
- The shared API (`src/dss/contracts.py` and the signatures in the contract) is
  **v0.2**. If a signature must be extended, prefer keyword-only parameters with
  defaults so existing positional calls keep working.
- Mathematical modules must not import Qt or Matplotlib. Dependency direction:
  `contracts → analytical/numerical/visualization → ui`.
- Do not copy another person's module and create a second implementation.

## Tests

Run the full test suite in headless mode.

PowerShell:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:QT_QPA_PLATFORM
```

POSIX:

```sh
QT_QPA_PLATFORM=offscreen MPLBACKEND=Agg python -m pytest -q
```

- Use the Agg backend for plotting tests (`MPLBACKEND=Agg`).
- CI runs on Windows with Python 3.11, the version `.python-version` pins.
- Do not use Python 3.12. PySide6 6.12.0's import hook fails on `six.moves`
  there, so `tests/ui` cannot be collected and the application does not start
  at all. This is not caused by the repository and reproduces on an unmodified
  checkout; the one-line reproduction is
  `python -c "import PySide6.QtWidgets; import matplotlib.dates"`.
- Person 3 also performs an interactive test in a native desktop session.

## Milestone Completion

A milestone is complete when all five conditions are met:

- [ ] Its acceptance criteria are satisfied.
- [ ] Tests pass and their output is recorded.
- [ ] Relevant implementation notes or measured results are recorded in
      `docs/evidence/` when applicable.
- [ ] Compatibility with the shared API is reviewed.
- [ ] The pull request has been reviewed.

**Passing tests alone does not prove compliance with the lab assignment.** For
changes that generate plots, inspect the output visually as well; automated
tests cannot determine whether a figure is readable.
