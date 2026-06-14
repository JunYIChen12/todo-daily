# Architect Output

## Current Behavior

`todo-daily` is a local Windows todo tool with a static browser UI and a Python background server. The frontend stores todos locally and syncs through `/api/store`. The backend serves static files, persists `todo-data/store.json`, checks reminders in the background, registers Windows toast support, and falls back to balloon notifications.

The current test entry point is:

```powershell
py -m unittest discover -s tests -v
```

## Redundancy And Complexity Sources

1. `todo_server.py` repeats subprocess invocation setup for PowerShell notification scripts in `ensure_notification_registration`, `show_windows_toast`, and `show_balloon_notification`.
2. Reminder logic mixes several concerns inside `check_due_reminders`: loading data, pruning old notification keys, parsing todo times, deciding due windows, sending notifications, and writing state.
3. Store normalization and recurring todo expansion are important behavior but currently have limited direct regression coverage.
4. `app.js` has parallel concepts for store normalization, recurring expansion, and due reminders. That duplication is cross-runtime and not a good first refactor target because sharing code would require a new runtime/build boundary.

## Files To Modify

- `todo_server.py`
  - add focused helpers for PowerShell command execution and reminder calculations
  - keep existing public endpoints and notification behavior unchanged
- `tests/test_notification_support.py`
  - keep existing tests
- `tests/test_store_and_reminders.py`
  - add regression coverage for store normalization, recurring expansion, due reminder parsing, stale notification pruning, and empty-store protection if practical

## Features That Must Remain Unchanged

- Static UI behavior and visible text.
- `/api/store`, `/api/status`, and `/api/test-notification` response semantics.
- Store file location under `todo-data/`.
- Reminder catch-up window: from scheduled time through `REMINDER_CATCH_UP_MINUTES`.
- Notification fallback order: Windows toast first, balloon fallback second.
- Existing script names and packaging/startup behavior.
- Refusal to replace a non-empty server store with an empty store.

## Refactor Boundary

This slice should stay inside Python backend helper extraction and tests. It should not:

- change `app.js`, `index.html`, `styles.css`, or scripts
- add dependencies
- move storage paths
- change notification text intentionally
- alter reminder timing rules
- introduce a new frontend/backend shared schema layer

## Risk Before Editing

Touching `todo_server.py` can affect local persistence and reminders. The safe path is to extract pure helpers first, add tests around current behavior, and keep endpoint and subprocess command arguments equivalent.

## Verification Strategy

Run:

```powershell
py -m compileall todo_server.py tests
py -m unittest discover -s tests -v
git diff --check
git status --short --branch --ignored
```

After PR creation, verify GitHub Actions CI for the PR.

## Phased Implementation Plan

1. Add regression tests for backend store/reminder helper behavior before changing implementation.
2. Extract pure reminder helpers:
   - stale notification key selection
   - time parsing/minute conversion
   - due-window predicate
   - reminder key creation
3. Extract one subprocess helper for PowerShell invocation while preserving command arguments and timeouts.
4. Run tests after each coherent slice.
5. Commit the scoped change, push, open a PR, and wait for CI.

## Developer Assignment

Implement phase 1 through phase 3 only. Prefer a compact diff with behavior-preserving helper extraction and focused tests. Stop if credible regression coverage cannot be established.
