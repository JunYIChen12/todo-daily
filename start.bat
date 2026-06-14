@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8765/api/status' -TimeoutSec 2 | Out-Null } catch { Start-Process powershell.exe -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-WindowStyle','Hidden','-File','%~dp0run-background.ps1') -WorkingDirectory '%~dp0' -WindowStyle Hidden; Start-Sleep -Seconds 2 }; Start-Process 'http://127.0.0.1:8765/index.html'"
