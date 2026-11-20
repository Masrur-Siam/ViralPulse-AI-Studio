$DesktopPath = Join-Path $env:USERPROFILE "Desktop"
if (-not (Test-Path $DesktopPath -ErrorAction SilentlyContinue)) {
    $DesktopPath = [Environment]::GetFolderPath("Desktop")
}
if (-not $DesktopPath) {
    $DesktopPath = "C:\Users\seaim\Desktop"
}

$WshShell = New-Object -ComObject WScript.Shell
$ShortcutPath = Join-Path $DesktopPath "ViralPulse AI Studio.lnk"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) { $ScriptDir = (Get-Location).Path }
$TargetBat = Join-Path $ScriptDir "Launch_ViralPulse.bat"
$WorkingDir = $ScriptDir

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetBat
$Shortcut.WorkingDirectory = $WorkingDir
$Shortcut.Description = "Launch ViralPulse AI Studio (One-Click)"
$Shortcut.IconLocation = "shell32.dll,137"
$Shortcut.WindowStyle = 1
$Shortcut.Save()

Write-Host "Created Desktop Shortcut successfully at: $ShortcutPath"
