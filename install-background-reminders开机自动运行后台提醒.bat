@echo off
setlocal
set "TASK_NAME=Daily Todo Background Reminders"
set "SCRIPT=%~dp0run-background.ps1"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$startup=[Environment]::GetFolderPath('Startup'); $shortcut=Join-Path $startup 'Daily Todo Background Reminders.lnk'; $shell=New-Object -ComObject WScript.Shell; $link=$shell.CreateShortcut($shortcut); $link.TargetPath='powershell.exe'; $link.Arguments='-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""%SCRIPT%""'; $link.WorkingDirectory='%~dp0'; $link.WindowStyle=7; $link.Save()"
if errorlevel 1 (
  echo Failed to create Startup shortcut.
  pause
  exit /b 1
)
schtasks /Create /TN "%TASK_NAME%" /SC ONLOGON /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""%SCRIPT%""" /F
if errorlevel 1 (
  echo Scheduled task failed, but Startup shortcut was created.
  echo Background reminders will start from your Startup folder when you sign in to Windows.
  pause
  exit /b 0
)
echo Background reminders will start from your Startup folder when you sign in to Windows.
echo A scheduled task was also created as a secondary startup path.
echo You can still use start.bat to open the todo page now.
pause
