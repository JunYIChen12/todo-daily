# Acceptance Tester Prompt Draft

You are executing `2026-06-14-strict-architecture-rebuild/T1` for `D:\codex\02_每日待办工具\todo-daily`.

You are a separate Acceptance Tester thread. Confirm cwd/repo root. Do not implement fixes. Do not edit product code, tests, CI, package/runtime config, `todo-data`, Controller state, Architect output, or Developer output.

Allowed write:
- `docs/workflows/2026-06-14-strict-architecture-rebuild/acceptance-output.md`

Read:
- `workflow-state.md`
- `session-registry.md`
- `architect-output.md`
- `developer-output.md`
- project `AGENTS.md`
- project `README.md`

Verify:
- Real role thread IDs exist for Controller, Architect, Developer, and this Acceptance Tester.
- Controller did not write product files or worker outputs.
- Developer did not self-accept.
- Diff only removes old workflow trace dirs and adds current strict workflow evidence.
- No product/runtime/test/CI/script/data files changed.
- `todo-data/` and caches remain untracked/ignored.
- Metrics vs baseline:
  - tracked bytes baseline 112,529; target <= 101,276
  - filtered worktree bytes baseline 113,871; target <= 102,483
- Run:
  - `py -m compileall todo_server.py tests`
  - `py -m unittest discover -s tests -v`
  - `git diff --check`
- Recompute metrics independently.

Write `acceptance-output.md` with status, actual thread id if visible, verification commands/results, metrics, changed/unchanged files, workflow validity, risks, and whether this is accepted for PR.
