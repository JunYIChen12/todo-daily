# Workflow State: todo-daily GitHub Collaboration Bootstrap

- Workflow ID: `2026-06-14-github-collaboration-bootstrap`
- Project path: `D:\codex\02_每日待办工具\todo-daily`
- Remote repo: `https://github.com/JunYIChen12/todo-daily.git`
- Phase: `implementation / github-bootstrap`
- Controller: current Codex session
- Last updated: 2026-06-14

## Goal

Convert the local `todo-daily` project into a GitHub collaboration-ready repository without changing existing app behavior.

## Current Facts

- Local project exists but is not a Git repository.
- Remote GitHub repository exists and is empty: no default branch, no commits, no issues, no pull requests.
- The app is a local Windows daily todo tool with:
  - static frontend: `index.html`, `styles.css`, `app.js`
  - Python backend: `todo_server.py`
  - Windows helper scripts and packaging scripts
  - tests under `tests/`
- The project has no `README.md`, no `AGENTS.md`, no `.gitignore`, no GitHub Actions workflow, and no package manifest.
- Runtime and cache files exist locally and must not be committed:
  - `todo-data/store.json`
  - `todo-data/notified.json`
  - `__pycache__/`
  - `tests/__pycache__/`

## Baseline Verification

- `py --version`: Python 3.14.4
- `py -m unittest discover -s tests -v`: passed, 4 tests
- `python --version`: failed locally because `python.exe` points to the WindowsApps placeholder

## Existing Behavior To Preserve

- Creating, editing, filtering, searching, and completing todos.
- Per-day todo state and recurring todo behavior.
- Local server persistence through `/api/store`.
- Reminder behavior and Windows notification fallback behavior.
- Background startup and tray helper scripts.
- Existing package creation and installation scripts.
- Existing notification support tests.

## Controller Guardrails

Allowed during Controller setup:

- Add workflow coordination files under this workflow directory.
- Inspect local files, Git status, and GitHub repository state.
- Run non-mutating verification commands.

Requires explicit human authorization:

- Initialize a local Git repository.
- Add or change Git remotes.
- Commit local files.
- Push to GitHub.
- Create, update, close, or merge GitHub issues and pull requests.
- Delete, move, or rewrite existing product files or user data.
- Add dependencies, change runtime requirements, or introduce CI/CD behavior beyond a proposed plan.

## Known Risks

- `todo-data/` contains real local app data and the remote repository is public.
- `__pycache__/` files are generated artifacts and should not be committed.
- The remote repository is empty, so the first push may create the default branch and becomes the base for all later collaboration.
- Local `python` is not reliable on this machine; local verification currently uses `py`.
- The HTML file displays mojibake in the terminal output. This may be a console decoding artifact or a real file encoding issue. It is out of scope for GitHub bootstrap unless the human asks to fix it.

## Role Status

| Role | Status | Notes |
| --- | --- | --- |
| Human owner | Active | Provides product decisions and authorizes remote mutation. |
| Controller | Active | Owns workflow state, boundaries, and role routing. |
| Architect | Pending | Should design the GitHub collaboration bootstrap plan. |
| Developer | Waiting | Should implement only after Architect output and human authorization. |
| Acceptance Tester | Waiting | Should verify after implementation and before remote mutation or PR merge. |

## Next Step

Implement the GitHub collaboration baseline, verify locally, push to the empty remote, and verify CI.

## Program Backlog

current:
- Implement baseline collaboration files.
- Initialize Git and push `main`.
- Verify GitHub Actions CI.

completed:
- Controller state created.
- Architect plan written.
- Baseline local tests passed before implementation.

pending:
- Optional follow-up PR proof after initial `main` exists.

blocked:
- None.
