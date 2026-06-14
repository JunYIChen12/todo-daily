# A1 Architect Output

status: complete
thread_id: 019ec4f9-1cae-72e0-b92a-07e399b12f44
cwd/repo_root: confirmed target todo-daily repo
trigger: Controller setup complete; read-only architecture plan requested.
role_only: yes. Edited only this file. No product/test/CI/script/package/runtime/data or downstream/control-state edits; no `todo-data/` content reads.

## Recommendation

Phased refactor. Phase 1: meet 10% size target by pruning obsolete tracked workflow trace, not runtime code. Phase 2: optional product simplification after targeted tests. Do not mix doc pruning with frontend/server rewrites.

Reason: behavior risk is in `app.js`, `todo_server.py`, Windows scripts, persistence, reminders, and notifications. Old workflow docs are large non-runtime files.

## Preserve

Files: `app.js`, `index.html`, `styles.css`, `todo_server.py`, `tests/**`, CI, scripts, install/startup/tray/package files, core docs/ADR, `todo-data/**`.

Features: todo CRUD/edit/search/filter/complete/delete, recurring per-day/delete/stop, localStorage fallback, `/api/store`, empty-store protection, reminders, Windows toast/fallback, `/api/status`, `/api/test-notification`, install/startup/tray/package flows, CI tests.

## Developer Scope

Allowed after Controller acceptance: prune/compact `docs/workflows/2026-06-14-architecture-simplification/**`; also `docs/workflows/2026-06-14-github-collaboration-bootstrap/**` if needed/approved; write `developer-output.md`; optional summary if chosen.

Forbidden: `todo-data/**`, product source, tests, CI, scripts, package/runtime/startup/install files, this file, `acceptance-output.md`, Controller state unless assigned.

Developer must confirm cwd/root/branch/status, measure size before/after, change only approved old workflow trace, run verification, and report files/metrics/proof/risks/no behavior change.

## Size Strategy

Baseline targets: tracked 112,529 -> <=101,276; worktree 113,871 -> <=102,483. Safe target is old workflow trace. `2026-06-14-architecture-simplification` is ~12.9 KB and can clear tracked target before new strict evidence. For margin, also prune/compact `2026-06-14-github-collaboration-bootstrap`; both old dirs are ~37 KB. Risk: low product, medium history/metric, high runtime-rewrite.

## Tests

Before/after Developer edits: `git status --short --branch`; recompute both size metrics; `py -m compileall todo_server.py tests`; `py -m unittest discover -s tests -v`; `git diff --check`; confirm `todo-data/` ignored/untracked without reading contents. If Phase 2 touches product behavior, add tests first plus manual/browser checks for CRUD, recurring, filters/search, sync, reminders, notifications.

## Human Gates

Ask before contested history delete/compaction; dependency/build/runtime/schema changes; touching `todo-data`; changing UI, recurring, reminder, persistence, API, notification, startup, packaging, or CI behavior; publishing strict trace if it blocks 10%; remote merge/delete outside authorization.

## Noise

Exact project-path launch failed; parent `D:\codex` used. Some paths showed mojibake; cwd/root confirmed. One PowerShell `rg *.ps1 *.bat` glob failed. Byte inventory had fatal messages for quoted non-ASCII zero-byte `.bat` paths; conclusion used workflow-doc sizes. Source-doc and cross-model review skipped/not needed: no framework implementation and Controller requested closeout.

efficiency: read-only parallel file reads; no product tests run by Architect; only this file rewritten.
