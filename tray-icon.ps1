param(
  [Parameter(Mandatory = $true)]
  [int]$ParentPid,
  [Parameter(Mandatory = $true)]
  [string]$LauncherPath,
  [Parameter(Mandatory = $true)]
  [string]$WorkingDirectory
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

function Start-TodoDaily {
  if ($LauncherPath.EndsWith(".bat", [System.StringComparison]::OrdinalIgnoreCase) -or
      $LauncherPath.EndsWith(".cmd", [System.StringComparison]::OrdinalIgnoreCase)) {
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$LauncherPath`"" -WorkingDirectory $WorkingDirectory | Out-Null
    return
  }

  Start-Process -FilePath $LauncherPath -WorkingDirectory $WorkingDirectory | Out-Null
}

$context = New-Object System.Windows.Forms.ApplicationContext
$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.Text = "Daily Todo background reminder"

$menu = New-Object System.Windows.Forms.ContextMenuStrip
$openItem = $menu.Items.Add("Open Daily Todo")
$hideItem = $menu.Items.Add("Hide tray icon")

$openItem.add_Click({ Start-TodoDaily })
$hideItem.add_Click({
  $notify.Visible = $false
  $notify.Dispose()
  $context.ExitThread()
})

$notify.ContextMenuStrip = $menu
$notify.add_DoubleClick({ Start-TodoDaily })
$notify.Visible = $true
$notify.ShowBalloonTip(4000, "Daily Todo", "Background reminders are running. Double-click to open.", [System.Windows.Forms.ToolTipIcon]::Info)

$monitor = New-Object System.Windows.Forms.Timer
$monitor.Interval = 5000
$monitor.add_Tick({
  if (-not (Get-Process -Id $ParentPid -ErrorAction SilentlyContinue)) {
    $monitor.Stop()
    $notify.Visible = $false
    $notify.Dispose()
    $context.ExitThread()
  }
})
$monitor.Start()

[System.Windows.Forms.Application]::Run($context)
