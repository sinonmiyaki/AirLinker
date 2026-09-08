# Run explicitly as Administrator on the Windows receiver. Never changes network profile.
param([string]$EnginePath = (Join-Path $PSScriptRoot 'runtime\bin\uxplay.exe'), [switch]$Remove)
$ErrorActionPreference = 'Stop'
$names = @('AirLinker-TCP', 'AirLinker-UDP', 'AirLinker-mDNS')
if ($Remove) {
  foreach ($name in $names) { Get-NetFirewallRule -Name $name -ErrorAction SilentlyContinue | Remove-NetFirewallRule }
  return
}
$engine = (Resolve-Path $EnginePath).Path
foreach ($name in $names) { Get-NetFirewallRule -Name $name -ErrorAction SilentlyContinue | Remove-NetFirewallRule }
New-NetFirewallRule -Name $names[0] -DisplayName 'AirLinker TCP' -Direction Inbound -Action Allow -Profile Private -Program $engine -Protocol TCP -LocalPort 35000-35002 -RemoteAddress LocalSubnet | Out-Null
New-NetFirewallRule -Name $names[1] -DisplayName 'AirLinker UDP' -Direction Inbound -Action Allow -Profile Private -Program $engine -Protocol UDP -LocalPort 35000-35002 -RemoteAddress LocalSubnet | Out-Null
New-NetFirewallRule -Name $names[2] -DisplayName 'AirLinker discovery' -Direction Inbound -Action Allow -Profile Private -Program $engine -Protocol UDP -LocalPort 5353 -RemoteAddress LocalSubnet | Out-Null
Write-Host 'AirLinker is allowed on private local networks.'
