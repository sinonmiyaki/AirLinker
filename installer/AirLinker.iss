#define AppVersion "0.1.1"
[Setup]
AppId={{9DA55A62-8351-4F78-9AD9-EAD01D96EE4D}
AppName=AirLinker
AppVersion={#AppVersion}
DefaultDirName={autopf}\AirLinker
DefaultGroupName=AirLinker
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=AirLinker-Setup-{#AppVersion}-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64os
ArchitecturesInstallIn64BitMode=x64os
MinVersion=10.0
PrivilegesRequired=admin
UninstallDisplayIcon={app}\AirLinker.exe
CloseApplications=yes
CloseApplicationsFilter=AirLinker.exe,uxplay.exe

[Files]
Source: "..\dist\AirLinker\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\AirLinker"; Filename: "{app}\AirLinker.exe"
Name: "{autodesktop}\AirLinker"; Filename: "{app}\AirLinker.exe"

[Run]
Filename: "{sys}\WindowsPowerShell\v1.0\powershell.exe"; Parameters: "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File ""{app}\configure-firewall.ps1"""; Flags: runhidden waituntilterminated
Filename: "{app}\AirLinker.exe"; Description: "AirLinker"; Flags: nowait postinstall skipifsilent runasoriginaluser

[UninstallRun]
Filename: "{sys}\WindowsPowerShell\v1.0\powershell.exe"; Parameters: "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File ""{app}\configure-firewall.ps1"" -Remove"; Flags: runhidden waituntilterminated; RunOnceId: "RemoveAirLinkerFirewall"
