@echo off
setlocal
set "TASK_NAME=Daily Todo Background Reminders"
schtasks /Delete /TN "%TASK_NAME%" /F
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$shortcut=Join-Path ([Environment]::GetFolderPath('Startup')) 'Daily Todo Background Reminders.lnk'; if (Test-Path -LiteralPath $shortcut) { Remove-Item -LiteralPath $shortcut -Force }"
if errorlevel 1 (
  echo Scheduled task was not removed. Startup shortcut cleanup was still attempted.
  pause
  exit /b 0
)
echo Background reminders have been removed from Windows startup.
pause
