# Developer Output

## Status

Complete locally; waiting for Acceptance Tester.

## Changed Files

- `todo_server.py`
- `tests/test_notification_support.py`
- `tests/test_store_and_reminders.py`
- `docs/workflows/2026-06-14-architecture-simplification/*`

## What Changed

- Extracted shared PowerShell subprocess setup into `run_powershell`.
- Reused `run_powershell` from toast shortcut registration, Windows toast sending, and balloon fallback notification.
- Extracted reminder helper logic:
  - `notification_keys_before`
  - `todo_time_minutes`
  - `is_reminder_due`
  - `reminder_key`
- Kept `/api/store`, notification fallback order, reminder timing window, and storage paths unchanged.
- Added regression tests for:
  - store normalization and legacy store migration
  - daily plus recurring todo expansion
  - reminder notification, old notification-key pruning, invalid time skipping, completed-task skipping
  - Windows toast PowerShell argument construction

## Verification Run

```powershell
py -m compileall todo_server.py tests
py -m unittest discover -s tests -v
git diff --check
git status --short --branch --ignored
```

Results:

- Compile check passed.
- Unit tests passed: 8 tests.
- `git diff --check` passed with line-ending warnings only.
- Git status shows intended modified/new files plus ignored `__pycache__/`, `tests/__pycache__/`, and `todo-data/`.

## Intentionally Not Changed

- No frontend files were changed.
- No startup, installer, tray, or packaging scripts were changed.
- No dependency or runtime framework was added.
- No runtime data was deleted, moved, or staged.
- No product semantics were intentionally changed.

## Remaining Developer Risks

- Windows notification display itself was not manually exercised; the tests verify command construction and existing fallback behavior.
- Browser UI behavior was not changed or browser-tested because this slice is backend helper extraction only.
