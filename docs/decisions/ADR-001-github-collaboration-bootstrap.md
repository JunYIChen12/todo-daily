# ADR-001: GitHub Bootstrap
Accepted 2026-06-14. The app was local and the GitHub repo was empty. Decision: create `main` with `.gitignore`, README, AGENTS, and CI; exclude `todo-data/`, caches, logs, artifacts, package zips, secrets, and env files; use PR branches after bootstrap. Runtime data stays private; CI covers Python compile/unit tests, not full Windows notification/package runtime.
