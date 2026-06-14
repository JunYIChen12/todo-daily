# Shared Task

## Human Request

Convert the local project into GitHub collaboration.

- Local path: `D:\codex\02_每日待办工具\todo-daily`
- Remote repository: `https://github.com/JunYIChen12/todo-daily.git`

## Definition Of Done

The task is done only when:

- The project is a clean local Git repository.
- Private runtime data and generated files are excluded from version control.
- The remote repository has a safe initial collaboration baseline.
- A human-readable `README.md` explains how to run, test, and package the project.
- Project rules are documented in `AGENTS.md`.
- CI or an equivalent verification path is available for future contributors.
- Existing related tests pass.
- Existing app behavior is not changed unless separately requested.

## Proposed Scope

Likely in scope after human approval:

- Create `.gitignore`.
- Create `README.md`.
- Create project-level `AGENTS.md`.
- Create `.github/workflows/ci.yml`.
- Initialize Git locally.
- Add remote `origin`.
- Create an initial commit.
- Push the initial collaboration baseline to GitHub.

Out of scope unless separately requested:

- Rewriting app UI or server logic.
- Fixing visible text encoding or copy.
- Refactoring Python or JavaScript structure.
- Changing packaging behavior.
- Migrating stored todo data.
- Adding new product features.

## Human Authorization Points

The human must explicitly authorize:

- Whether to push an initial `main` branch directly to the empty remote, or use a temporary bootstrap branch and pull request.
- Whether local runtime data in `todo-data/` should remain only on this machine.
- Whether GitHub Issues and Pull Requests should be created during this test.
- Whether CI should use only Python unit tests or also add packaging checks.

## Verification Baseline

Current known-good local command:

```powershell
py -m unittest discover -s tests -v
```

Current result:

```text
Ran 4 tests in 0.001s
OK
```
