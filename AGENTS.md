# AGENTS.md

## Project Goal

This is a production local Windows todo tool. New collaboration, packaging, or feature work must not break existing completed behavior.

## Non-Negotiable Rules

1. Do not remove, rewrite, or simplify existing completed features unless explicitly requested.
2. Before changing product code, identify affected files and functions.
3. Prefer small, incremental changes over broad rewrites.
4. Do not create duplicate components, duplicate APIs, or duplicate utility functions.
5. Do not commit runtime data, generated caches, package artifacts, or temporary debug files.
6. If a change may affect reminders, local persistence, packaging, or startup behavior, explain the risk before editing.
7. After editing, run relevant tests and a regression checklist.
8. If tests do not cover touched behavior, add minimal regression coverage where practical.

## Local Data Boundary

The `todo-data/` directory contains local user data and must stay out of GitHub.

Generated files such as `__pycache__/`, `artifacts/`, `build/`, `dist/`, package zip files, and logs must also stay out of GitHub.

## Required Verification

At minimum, run:

```powershell
py -m unittest discover -s tests -v
```

For packaging changes, also run the relevant packaging script or document why it could not be run.

## Collaboration Workflow

- Use short-lived branches after the initial repository bootstrap.
- Keep commits scoped and descriptive.
- Open pull requests for review before merging to `main`.
- Keep `main` in a working state.
- Do not push private runtime data or secrets.

## Existing Features To Preserve

- Daily todo creation, editing, filtering, search, completion, and deletion.
- Recurring todo behavior.
- Local persistence through `todo_server.py` and `/api/store`.
- Background reminders.
- Windows toast notification registration and fallback notification behavior.
- Installer, startup, and packaging scripts.
