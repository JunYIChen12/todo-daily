# Agent Registry

Workflow ID: `2026-06-14-github-collaboration-bootstrap`

## Roles

| Role | Owner | Trigger | Allowed writes | Required output | Status |
| --- | --- | --- | --- | --- | --- |
| Controller | Current Codex session | Human starts or resumes workflow | `workflow-state.md`, `agent-registry.md`, `shared-task.md`, `session-registry.md` | Current workflow state and next-role prompt | Active |
| Architect | Separate Codex dialog or current session acting as Architect | Controller assigns architecture planning | `architect-output.md` only | Bootstrap plan, risk review, file list, verification plan | Pending |
| Developer | Separate Codex dialog or current session acting as Developer | Human approves Architect plan | Implementation files approved by Controller and human | Patch summary, commands run, risks | Waiting |
| Acceptance Tester | Separate Codex dialog or current session acting as Tester | Developer says implementation is ready | `acceptance-output.md` only | Verification result and release recommendation | Waiting |
| Human owner | User | Any decision boundary | N/A | Scope decisions and remote authorization | Active |

## Ownership Rules

- The Controller is the only role that updates `workflow-state.md` and `session-registry.md`.
- Worker roles must not modify workflow state directly.
- Worker roles must write their conclusions to their assigned output file.
- No role may push to GitHub, create issues, create pull requests, or merge changes without explicit human authorization.
- Product files must not be rewritten or simplified unless the human explicitly requests it.

## Codex App Note

If the exact project folder cannot be opened as a saved Codex project, use projectless fallback:

- State the exact project path in every worker prompt.
- Require the worker to `cd` into `D:\codex\02_每日待办工具\todo-daily`.
- Require the worker to read this workflow directory first.
- Require the worker to report the files it inspected and the files it intends to change.
