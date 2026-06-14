# ADR-001: Bootstrap GitHub Collaboration

## Status

Accepted

## Date

2026-06-14

## Context

The project existed locally as a Windows todo tool but was not yet a Git repository. A public empty GitHub repository already existed at `https://github.com/JunYIChen12/todo-daily.git`.

The local directory also contained runtime data under `todo-data/` and generated Python cache files. Those files must not be published because they are either private local state or generated artifacts.

## Decision

Bootstrap the repository with a minimal collaboration baseline:

- Initialize local Git on `main`.
- Add `.gitignore` before the first commit.
- Exclude runtime data, caches, logs, package artifacts, and local environment files.
- Add `README.md` with run, test, packaging, and collaboration instructions.
- Add project-level `AGENTS.md` for future agent/human contributors.
- Add GitHub Actions CI for Python compile and unit-test verification.
- Push the initial baseline to `main` because the remote repository is empty and has no existing branch to target with a pull request.
- Use short-lived branches and pull requests for follow-up changes after the initial baseline exists.

## Alternatives Considered

### Create a bootstrap branch first

This is the normal collaboration style once a base branch exists. It was not selected for the first commit because the remote repository was empty and had no `main` branch for a pull request target.

### Commit only source files without docs or CI

Rejected. A GitHub collaboration baseline should include run instructions, contribution boundaries, and automated verification from the first published state.

### Include `todo-data/`

Rejected. The directory contains local user data and should remain machine-local.

## Consequences

- The first push creates the public collaboration baseline.
- Future work can use issues, branches, pull requests, and CI checks.
- Local runtime data remains private.
- CI currently verifies Python syntax and the existing unit tests, but it does not exercise the Windows notification runtime or package creation scripts.
