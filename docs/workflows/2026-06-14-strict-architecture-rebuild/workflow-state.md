# Workflow State: Strict Architecture Rebuild

## Identity

- workflow_slug: `2026-06-14-strict-architecture-rebuild`
- controller_thread: `019ec4f3-fa64-7eb2-928f-198a708592ed`
- project: `D:\codex\02_每日待办工具\todo-daily`
- repo: `JunYIChen12/todo-daily`
- baseline_head: `0b6877a927544135df7512cd7594299f22455208`
- mode: `strict-multi-dialog`

## Rules

- Controller owns only state/registries/prompts in this workflow directory.
- Controller must not edit product code, tests, CI, package/runtime config, user data, or worker outputs.
- Required real role threads: Architect, Developer, Acceptance Tester.
- `todo-data/` is private user data; do not read contents, delete, migrate, commit, or use for size reduction.

## Current Behavior To Preserve

- Static UI: `index.html`, `styles.css`, `app.js`.
- Backend/store/reminders/notifications: `todo_server.py`.
- Windows install/startup/background/tray/toast/packaging scripts.
- Tests: `py -m unittest discover -s tests -v`.
- Features: todo CRUD/search/filter/completion/delete, recurring todos, `/api/store`, empty-store overwrite guard, reminders, toast and fallback notifications.

## Size Baseline

Policy:
- tracked bytes: sum `git cat-file -s` for every blob in `git ls-files -s`.
- filtered worktree bytes: sum files excluding `.git`, `todo-data`, `__pycache__`, `artifacts`, `build`, `dist`, `.pytest_cache`, `node_modules`.

Baseline before this workflow:
- tracked files: 36
- tracked bytes: 112,529
- filtered worktree files: 36
- filtered worktree bytes: 113,871

Targets:
- tracked bytes <= 101,276
- filtered worktree bytes <= 102,483

## Role Registry

| Role | Output | Thread | Status | Notes |
| --- | --- | --- | --- | --- |
| Controller | `workflow-state.md`, `session-registry.md` | `019ec4f3-fa64-7eb2-928f-198a708592ed` | active | no product writes |
| Architect | `architect-output.md` | `019ec4f9-1cae-72e0-b92a-07e399b12f44` | verified | phased cleanup recommended |
| Developer | `developer-output.md` | `019ec4fe-9b81-75d2-a5de-252d26b25029` | verified-for-acceptance | tracked and filtered worktree metrics pass after evidence compaction |
| Acceptance Tester | `acceptance-output.md` | `019ec506-8cfb-7740-a9e1-2515a5698299` | accepted | independent verification passed |

## Progress

Completed:
- Read control-console rules, project AGENTS/README/docs/workflows/CI/tests.
- Baseline local tests passed: 8 tests.
- Created real Architect thread and accepted output.
- Created real Developer thread.
- Developer staged deletion of obsolete workflow trace directories only:
  - `docs/workflows/2026-06-14-architecture-simplification/**`
  - `docs/workflows/2026-06-14-github-collaboration-bootstrap/**`
- Developer verification passed: compileall, unittest, diff check.

Current:
- Create branch, commit, PR, and wait for CI.

Pending:
- Acceptance verifies diff, metrics, tests, data boundary, strict workflow evidence.
- Controller creates branch/commit/PR, waits for CI, merges only after acceptance and CI.

## Metrics From Developer

- Baseline tracked bytes: 112,529.
- Post-cleanup tracked bytes: 78,790, reduction 29.98%, target passed.
- Baseline filtered worktree bytes: 113,871.
- Post-cleanup filtered worktree before Developer output: 121,363, target not yet passed because active strict workflow evidence is counted.
- After Controller-owned prompt/state compaction and role-owned output compaction: filtered worktree bytes 93,439, target passed.
- Final Controller recompute after acceptance output: tracked index bytes 78,790; filtered worktree bytes 96,801; both targets passed.

## Evidence Notes

- `git status` before workflow: clean on `main...origin/main`.
- `origin/main`: `0b6877a927544135df7512cd7594299f22455208`.
- Baseline `py -m unittest discover -s tests -v`: passed, 8 tests.
- Exact subproject was not a saved Codex project; role threads launched from saved parent project `D:\codex` and confirmed target repo path.

## Workflow Validation

- real_controller_thread: `019ec4f3-fa64-7eb2-928f-198a708592ed`
- real_architect_thread: `019ec4f9-1cae-72e0-b92a-07e399b12f44`
- real_developer_thread: `019ec4fe-9b81-75d2-a5de-252d26b25029`
- real_acceptance_thread: `019ec506-8cfb-7740-a9e1-2515a5698299`
- strict_mode_result: accepted-locally
- controller_wrote_product_files: no
- controller_wrote_worker_outputs: no
- implementation_thread_self_accepted: no
- strict_mode_result: pending
