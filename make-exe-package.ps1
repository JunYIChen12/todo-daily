$ErrorActionPreference = "Stop"

$sourceDir = Split-Path -Parent $PSCommandPath
$artifactsDir = Join-Path $sourceDir "artifacts"
$buildDir = Join-Path $artifactsDir "build"
$distDir = Join-Path $artifactsDir "dist"
$packagesDir = Join-Path $artifactsDir "packages"
$zipPath = Join-Path $packagesDir "todo-daily-windows-exe.zip"
$packageRoot = Join-Path $env:TEMP "todo-daily-exe-package"
$appDir = Join-Path $packageRoot "todo-daily"

function Ensure-PyInstaller {
  cmd /c "py -m pip show pyinstaller >nul 2>nul"
  if ($LASTEXITCODE -eq 0) {
    return
  }

  Write-Host "Installing PyInstaller for packaging..."
  & py -m pip install --user pyinstaller
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to install PyInstaller."
  }
}

Ensure-PyInstaller

New-Item -ItemType Directory -Force -Path $buildDir, $distDir, $packagesDir | Out-Null

Push-Location $sourceDir
try {
  & py -m PyInstaller --noconfirm --clean --onefile --name TodoDailyServer --workpath $buildDir --distpath $distDir --specpath $artifactsDir todo_server.py
  if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed."
  }
} finally {
  Pop-Location
}

if (Test-Path $packageRoot) {
  Remove-Item -LiteralPath $packageRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $appDir | Out-Null

$files = @(
  "TodoDailyServer.exe",
  "index.html",
  "app.js",
  "styles.css",
  "start.bat",
  "install.bat",
  "run-background.ps1",
  "install.ps1",
  "PACKAGING.md"
)

foreach ($file in $files) {
  $source = if ($file -eq "TodoDailyServer.exe") {
    Join-Path $distDir "TodoDailyServer.exe"
  } else {
    Join-Path $sourceDir $file
  }
  Copy-Item -LiteralPath $source -Destination (Join-Path $appDir $file) -Force
}

New-Item -ItemType Directory -Force -Path (Join-Path $appDir "todo-data") | Out-Null

if (Test-Path $zipPath) {
  Remove-Item -LiteralPath $zipPath -Force
}
Compress-Archive -LiteralPath $appDir -DestinationPath $zipPath -Force

Write-Host "Created: $zipPath"
Write-Host "Recipient command after unzip:"
Write-Host 'powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1'
