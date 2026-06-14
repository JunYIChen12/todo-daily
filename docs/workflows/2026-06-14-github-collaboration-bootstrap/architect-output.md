# Architect Output

## Current Behavior Summary

`todo-daily` is a local Windows daily todo tool. It uses a static browser UI, a Python HTTP server for storage and background reminders, and PowerShell/Batch scripts for startup, notification registration, installation, and packaging.

Current tests cover notification launcher and toast fallback behavior. They pass locally with:

```powershell
py -m unittest discover -s tests -v
```

## Repository Bootstrap Strategy

Because the remote repository is empty, use a direct initial push to `main` for the first collaboration baseline. After that baseline exists, switch to short-lived branches and pull requests for follow-up changes.

## Files To Include

Include source, tests, scripts, docs, and collaboration configuration:

- `index.html`
- `styles.css`
- `app.js`
- `todo_server.py`
- `tests/`
- `*.ps1`
- `*.bat`
- `PACKAGING.md`
- `.gitignore`
- `README.md`
- `AGENTS.md`
- `.github/workflows/ci.yml`
- `docs/decisions/`
- `docs/workflows/2026-06-14-github-collaboration-bootstrap/`

## Files To Exclude

Exclude private local data and generated artifacts:

- `todo-data/`
- `__pycache__/`
- `tests/__pycache__/`
- `artifacts/`
- `build/`
- `dist/`
- `packages/`
- `*.zip`
- `*.spec`
- `.env*`
- `*.log`

## Proposed New Files

- `.gitignore`
- `README.md`
- `AGENTS.md`
- `.github/workflows/ci.yml`
- `docs/decisions/ADR-001-github-collaboration-bootstrap.md`

## CI Plan

Use GitHub Actions on `push` to `main` and `pull_request` targeting `main`.

The first CI scope should be intentionally small:

- Check out repository.
- Set up Python 3.13.
- Compile `todo_server.py` and `tests/`.
- Run `python -m unittest discover -s tests -v`.
- Assert local runtime data files are absent from the checkout.

Windows packaging verification can be added later in a separate workflow because it requires Windows-specific runtime assumptions and may need PyInstaller.

## Human Authorization Points

The human has authorized continuing until a verified conclusion. The following actions are now allowed for this run:

- initialize Git locally
- commit the collaboration baseline
- push the initial `main` branch to the empty remote
- create a follow-up issue and PR if needed to prove collaboration flow

Still out of scope:

- product behavior changes
- deleting local user data
- fixing text encoding or UI copy
- adding dependencies

## Developer Prompt

Implement the GitHub collaboration baseline without changing product behavior.

Required work:

- Add `.gitignore`, `README.md`, `AGENTS.md`, `.github/workflows/ci.yml`, and ADR documentation.
- Initialize Git on `main`.
- Verify ignored runtime data is not staged.
- Run `py -m unittest discover -s tests -v`.
- Commit and push the initial baseline to `https://github.com/JunYIChen12/todo-daily.git`.
- Check remote CI status.
