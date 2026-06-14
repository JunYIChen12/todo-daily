# Session Registry: Strict Architecture Rebuild

| Task | Role | Thread | Status | Proof | Next |
| --- | --- | --- | --- | --- | --- |
| C1 | Controller | `019ec4f3-fa64-7eb2-928f-198a708592ed` | active | state/registry only | launch T1 after compaction |
| A1 | Architect | `019ec4f9-1cae-72e0-b92a-07e399b12f44` | verified | `architect-output.md` | complete |
| D1 | Developer | `019ec4fe-9b81-75d2-a5de-252d26b25029` | verified-for-acceptance | `developer-output.md`; tests pass; metrics pass after compaction | launch T1 |
| T1 | Acceptance Tester | `019ec506-8cfb-7740-a9e1-2515a5698299` | accepted | `acceptance-output.md`; local checks and metrics pass | PR/CI |

## Launch Log

- C1 active in current thread.
- A1 exact subproject launch failed because only parent `D:\codex` was saved; parent-project launch succeeded with thread `019ec4f9-1cae-72e0-b92a-07e399b12f44`.
- D1 parent-project launch succeeded with thread `019ec4fe-9b81-75d2-a5de-252d26b25029`.
- T1 parent-project launch succeeded with thread `019ec506-8cfb-7740-a9e1-2515a5698299`.

## Noise

- Project launcher requires saved parent project, not the todo-daily subdirectory.
- Non-ASCII `.bat` filenames made path-based byte scripts noisy; blob-hash metrics avoided this.
- Active strict workflow evidence must be compacted to make the filtered worktree metric fair.
