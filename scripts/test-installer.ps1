$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$install = Join-Path $env:RUNNER_TEMP 'AirLinker-install-test'
$setup = (Resolve-Path 'dist/installer/AirLinker-Setup-0.1.0-x64.exe').Path
$p = Start-Process $setup -ArgumentList '/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',"/DIR=`"$install`"" -PassThru
if (!$p.WaitForExit(120000)) { $p.Kill(); throw 'Installer timed out' }
if ($p.ExitCode -ne 0) { throw "Installer returned $($p.ExitCode)" }
$env:QT_QPA_PLATFORM = 'offscreen'
$preview = Join-Path $env:RUNNER_TEMP 'AirLinker-installed.png'
$p = Start-Process (Join-Path $install 'AirLinker.exe') -ArgumentList '--screenshot',"`"$preview`"" -PassThru
if (!$p.WaitForExit(30000)) { $p.Kill(); throw 'Installed app timed out' }
if ($p.ExitCode -ne 0 -or !(Test-Path $preview)) { throw 'Installed app failed' }
foreach ($name in 'AirLinker-TCP','AirLinker-UDP','AirLinker-mDNS') {
    if (!(Get-NetFirewallRule -Name $name -ErrorAction SilentlyContinue)) { throw "Missing firewall rule $name" }
}
$p = Start-Process (Join-Path $install 'unins000.exe') -ArgumentList '/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART' -PassThru
if (!$p.WaitForExit(90000)) { $p.Kill(); throw 'Uninstaller timed out' }
if ($p.ExitCode -ne 0) { throw 'Uninstaller failed' }
if (Test-Path (Join-Path $install 'AirLinker.exe')) { throw 'Application was not removed' }
foreach ($name in 'AirLinker-TCP','AirLinker-UDP','AirLinker-mDNS') {
    if (Get-NetFirewallRule -Name $name -ErrorAction SilentlyContinue) { throw "Firewall rule not removed: $name" }
}
Write-Host 'Install, launch, firewall rules and uninstall passed.'
