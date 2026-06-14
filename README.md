# Daily Todo

Daily Todo is a local Windows todo tool with a static web UI, a small Python background server, Windows reminder support, and packaging scripts for non-developer users.

## Quick Start

On Windows:

```powershell
.\start.bat
```

The app opens at:

```text
http://127.0.0.1:8765/index.html
```

If the background server is not running, `start.bat` starts it through `run-background.ps1`.

## Project Structure

| Path | Purpose |
| --- | --- |
| `index.html` | Main app page |
| `styles.css` | UI styling |
| `app.js` | Browser-side todo behavior |
| `todo_server.py` | Local HTTP server, storage, reminder loop, notification helpers |
| `tests/` | Python unit tests |
| `*.ps1`, `*.bat` | Windows startup, install, notification, and packaging helpers |
| `PACKAGING.md` | Packaging instructions |

## Local Data

Runtime todo data is stored in `todo-data/` on the local machine. This directory is intentionally ignored by Git because it may contain private user data.

## Development Commands

Run tests locally on Windows:

```powershell
py -m unittest discover -s tests -v
```

The current local machine has `py` available. The plain `python` command may point to a WindowsApps placeholder, so prefer `py` for local verification here.

## Packaging

Build a package for users without Python:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\make-exe-package.ps1
```

Build a Python-based package:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\make-package.ps1
```

See `PACKAGING.md` for details.

## GitHub Collaboration

This repository uses a small collaboration baseline:

- `main` is the stable branch.
- Changes should be made on short-lived branches and reviewed through pull requests after the initial repository bootstrap.
- CI runs Python unit tests on pushes to `main` and pull requests targeting `main`.
- Runtime data, generated caches, and packaging artifacts must not be committed.

Before opening a pull request, run:

```powershell
py -m unittest discover -s tests -v
```
