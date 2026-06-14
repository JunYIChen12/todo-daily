# Daily Todo packaging

## No-programming-tools package

On the packaging machine, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\make-exe-package.ps1
```

This creates:

```text
artifacts\packages\todo-daily-windows-exe.zip
```

The recipient does not need Python, Node, Git, or any programming tools.

After unzip, the recipient runs this in the `todo-daily` folder:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

Or they can double-click `install.bat`.

The installer copies the app to `%LOCALAPPDATA%\TodoDaily`, registers startup task `Daily Todo Background Reminders`, starts the background service, and opens `http://127.0.0.1:8765/index.html`.

## Python package

If the recipient already has Python, you can also run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\make-package.ps1
```

This creates `artifacts\packages\todo-daily-windows-python.zip`.
