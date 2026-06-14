$ErrorActionPreference = "Stop"
$sourceDir = Split-Path -Parent $PSCommandPath
$artifactsDir = Join-Path $sourceDir "artifacts"
$packagesDir = Join-Path $artifactsDir "packages"
$packageRoot = Join-Path $env:TEMP "todo-daily-package"
$appDir = Join-Path $packageRoot "todo-daily"
$zipPath = Join-Path $packagesDir "todo-daily-windows-python.zip"
New-Item -ItemType Directory -Force -Path $packagesDir | Out-Null
if (Test-Path $packageRoot) {
Remove-Item -LiteralPath $packageRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $appDir | Out-Null
$excludeNames = @("todo-data", "__pycache__", "build", "dist", "packages", "artifacts", "todo-daily-windows-python.zip", "todo-daily-windows-exe.zip")
Get-ChildItem -LiteralPath $sourceDir -Force | Where-Object {
$excludeNames -notcontains $_.Name
} | ForEach-Object {
Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $appDir $_.Name) -Recurse -Force
}
if (Test-Path $zipPath) {
Remove-Item -LiteralPath $zipPath -Force
}
Compress-Archive -LiteralPath $appDir -DestinationPath $zipPath -Force
