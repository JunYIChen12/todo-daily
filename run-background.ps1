Set-Location -LiteralPath $PSScriptRoot

$rootExe = Join-Path $PSScriptRoot "TodoDailyServer.exe"
$pythonSource = Join-Path $PSScriptRoot "todo_server.py"
$statusUrl = "http://127.0.0.1:8765/api/status"

function Test-TodoDailyRunning {
  try {
    Invoke-WebRequest -UseBasicParsing -Uri $statusUrl -TimeoutSec 2 | Out-Null
    return $true
  } catch {
    return $false
  }
}

function Start-TodoDailyServer {
  if (Test-Path -LiteralPath $rootExe) {
    & $rootExe
    return
  }

  if (Test-Path -LiteralPath $pythonSource) {
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
      py $pythonSource
      return
    }

    python $pythonSource
    return
  }

  Start-Sleep -Seconds 60
}

while ($true) {
  if (Test-TodoDailyRunning) {
    Start-Sleep -Seconds 60
    continue
  }

  Start-TodoDailyServer
  Start-Sleep -Seconds 5
}
