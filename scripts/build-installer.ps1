param([string]$ISCC)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (!(Test-Path 'dist\AirLinker\AirLinker.exe') -or !(Test-Path 'dist\AirLinker\runtime\bin\uxplay.exe')) {
    throw 'Build the Windows application and receiver first.'
}
if (!$ISCC) {
    $found = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($found) { $ISCC = $found.Source }
    else {
        foreach ($version in 6,7) {
            $candidate = "${env:ProgramFiles(x86)}\Inno Setup $version\ISCC.exe"
            if (Test-Path $candidate) { $ISCC = $candidate; break }
        }
    }
}
if (!$ISCC) { throw 'Install Inno Setup 6 or 7, or pass -ISCC with the compiler path.' }
& $ISCC installer\AirLinker.iss
if ($LASTEXITCODE) { throw 'Installer compilation failed.' }
$setup = Get-Item dist\installer\AirLinker-Setup-0.1.2-x64.exe
$hash = (Get-FileHash $setup -Algorithm SHA256).Hash
"$hash  $($setup.Name)" | Set-Content "$($setup.FullName).sha256" -Encoding ascii
Write-Host $setup.FullName
