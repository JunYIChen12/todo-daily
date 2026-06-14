param(
[Parameter(Mandatory = $true)]
[string]$AppId,
[Parameter(Mandatory = $true)]
[string]$Title,
[Parameter(Mandatory = $true)]
[string]$Body
)
$ErrorActionPreference = "Stop"
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] > $null
$escapedTitle = [System.Security.SecurityElement]::Escape($Title)
$escapedBody = [System.Security.SecurityElement]::Escape($Body)
$toastXml = @"
<toast>
<visual>
<binding template="ToastGeneric">
<text>$escapedTitle</text>
<text>$escapedBody</text>
</binding>
</visual>
</toast>
"@
$xmlDocument = New-Object Windows.Data.Xml.Dom.XmlDocument
$xmlDocument.LoadXml($toastXml)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xmlDocument)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($AppId).Show($toast)
