# Workflow State: Architecture Simplification

- Workflow ID: `2026-06-14-architecture-simplification`
- Project path: `D:\codex\02_每日待办工具\todo-daily`
- Remote repo: `https://github.com/JunYIChen12/todo-daily`
- Branch: `codex/architecture-simplification`
- Phase: `pr-ci-verified`
- Controller: current Codex session
- Last updated: 2026-06-14

## Goal

Reduce real redundancy and complexity in `todo-daily` while preserving existing completed behavior.

## Current Behavior

- Static UI in `index.html`, `styles.css`, and `app.js`.
- Browser state persists to `localStorage` and syncs with `todo_server.py` through `/api/store`.
- Python server stores private runtime data under `todo-data/`.
- Daily todos and recurring todos are combined for reminder checks.
- Windows toast registration is attempted first; balloon notification is used as fallback.
- Existing tests cover notification launcher and toast fallback behavior.

## Project Constraints Capsule

source_files:
- `AGENTS.md`
- `README.md`
- `docs/workflows/2026-06-14-github-collaboration-bootstrap/*`

package_manager:
- None. This project currently uses Python stdlib, static frontend files, PowerShell, and Batch scripts.

verification_tiers:
- tier: `unit-or-component`
  use_when: Python helper refactors and tests
  commands:
  - `py -m compileall todo_server.py tests`
  - `py -m unittest discover -s tests -v`
- tier: `script-or-guard`
  use_when: Git hygiene and publication checks
  commands:
  - `git status --short --branch --ignored`
  - `git diff --check`

forbidden:
- Do not delete or commit `todo-data/`.
- Do not change product core semantics.
- Do not add unnecessary dependencies.
- Do not rewrite the UI or package scripts for this slice.
- Do not remove completed features for simplicity.

## Roles

| Role | Status | Allowed writes | Required output |
| --- | --- | --- | --- |
| Controller | Active | Workflow files, GitHub lifecycle, evidence reconciliation | `workflow-state.md`, `session-registry.md`, final closeout |
| Architect | Active | `architect-output.md` | Architecture diagnosis and phased plan |
| Developer | Waiting | Approved source/test files only | Small refactor, tests, proof |
| Acceptance Tester | Waiting | `acceptance-output.md` | Independent verification and release recommendation |

## Affected Files Under Consideration

- `todo_server.py`
  - `day_todos`
  - `check_due_reminders`
  - `ensure_notification_registration`
  - `show_windows_toast`
  - `show_balloon_notification`
- `tests/test_notification_support.py`
  - existing notification regression tests
- possible new test file under `tests/`

## Existing Features To Preserve

- Daily todo creation, editing, filtering, search, completion, and deletion.
- Recurring todo behavior, including per-day state and deletion/stop semantics.
- Local persistence through `/api/store`.
- Empty browser store must not overwrite non-empty server store.
- Background reminders and notification de-duplication.
- Windows toast notification registration and fallback notification behavior.
- Installer, startup, tray, and packaging scripts.

## Program Backlog

current:
- Finish Architect plan.

completed:
- Read project AGENTS/README/workflow docs.
- Checked Git state and remote state.
- Identified Python backend helper duplication as the first small slice.
- Created branch `codex/architecture-simplification`.
- Architect plan written.
- Developer backend helper refactor completed.
- Acceptance Tester local verification passed.
- Commit `aff94c9` pushed to `origin/codex/architecture-simplification`.
- Draft PR #3 created: `https://github.com/JunYIChen12/todo-daily/pull/3`.
- PR #3 CI run `27491038609` passed for commit `aff94c9`.

pending:
- Commit workflow evidence update.
- Re-run PR CI for evidence update.
- Merge PR after final CI remains green.

blocked:
- None.

## Controller Notes

- Direct Controller implementation is allowed for this run because the user explicitly authorized sequentially acting as Architect, Developer, and Acceptance Tester in the current thread. Role outputs must remain separated in files.
- The first refactor should prefer test-covered backend helpers over broad UI changes.
- The frontend may also have duplication around reminder due-window calculation, but changing browser behavior requires heavier runtime/UI validation and is deferred unless the backend slice proves too small.
