param(
[string]$InstallDir = "$env:LOCALAPPDATA\TodoDaily",
[switch]$NoStart
)
$ErrorActionPreference = "Stop"
function Copy-AppFiles {
param([string]$SourceDir, [string]$TargetDir)
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
$excludeNames = @("__pycache__", "todo-data", "build", "dist", "packages", "artifacts", "TodoDailyServer.spec", "todo-daily-windows.zip", "todo-daily-windows-exe.zip")
Get-ChildItem -LiteralPath $SourceDir -Force | Where-Object {
$excludeNames -notcontains $_.Name
} | ForEach-Object {
Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $TargetDir $_.Name) -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $TargetDir "todo-data") | Out-Null
}
function Register-StartupTask {
param([string]$TargetDir)
$taskName = "Daily Todo Background Reminders"
$scriptPath = Join-Path $TargetDir "run-background.ps1"
$action = New-ScheduledTaskAction `
-Execute "powershell.exe" `
-Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet `
-AllowStartIfOnBatteries `
-DontStopIfGoingOnBatteries `
-ExecutionTimeLimit (New-TimeSpan -Days 30) `
-MultipleInstances IgnoreNew
Register-ScheduledTask `
-TaskName $taskName `
-Action $action `
-Trigger $trigger `
-Settings $settings `
-Description "Daily Todo background reminder service" `
-Force | Out-Null
}
function Start-TodoDaily {
param([string]$TargetDir)
try {
Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8765/api/status" -TimeoutSec 2 | Out-Null
} catch {
Start-Process powershell.exe `
-ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden", "-File", (Join-Path $TargetDir "run-background.ps1")) `
-WorkingDirectory $TargetDir `
-WindowStyle Hidden
Start-Sleep -Seconds 2
}
Start-Process "http://127.0.0.1:8765/index.html"
}
$sourceDir = Split-Path -Parent $PSCommandPath
$exePath = Join-Path $sourceDir "TodoDailyServer.exe"
$artifactExePath = Join-Path $sourceDir "artifacts\dist\TodoDailyServer.exe"
$pythonSource = Join-Path $sourceDir "todo_server.py"
if (-not (Test-Path $exePath) -and -not (Test-Path $artifactExePath) -and -not (Test-Path $pythonSource)) {
throw "Neither TodoDailyServer.exe nor todo_server.py was found."
}
Copy-AppFiles -SourceDir $sourceDir -TargetDir $InstallDir
Register-StartupTask -TargetDir $InstallDir
if (-not $NoStart) {
Start-TodoDaily -TargetDir $InstallDir
}
