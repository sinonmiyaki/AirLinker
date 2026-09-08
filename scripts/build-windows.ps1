param([string]$MSYS2 = 'C:\msys64')
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (!(Test-Path "$MSYS2\usr\bin\bash.exe")) { throw 'Install MSYS2 from https://www.msys2.org first, then run pacman -Syu in its terminal.' }
$env:MSYSTEM = 'UCRT64'
$env:MSYS2_PATH_TYPE = 'inherit'
$env:CHERE_INVOKING = '1'
& "$MSYS2\usr\bin\bash.exe" -lc 'bash scripts/build-engine.sh'
if ($LASTEXITCODE) { throw 'Receiver build failed.' }
py -3.11 -m venv .venv
if ($LASTEXITCODE) { throw 'Install Python 3.11 x64 from python.org (including the py launcher).' }
& .venv\Scripts\python.exe -m pip install -r requirements.txt 'pyinstaller==6.12.0'
if ($LASTEXITCODE) { throw 'Python dependency installation failed.' }
& .venv\Scripts\python.exe -m unittest discover -s tests -v
if ($LASTEXITCODE) { throw 'Tests failed.' }
& .venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --onedir --name AirLinker run.py
if ($LASTEXITCODE) { throw 'Application packaging failed.' }
Copy-Item runtime dist\AirLinker\runtime -Recurse -Force
Copy-Item LICENSE,README.md,THIRD_PARTY_NOTICES.md dist\AirLinker
Copy-Item LICENSES dist/AirLinker/LICENSES -Recurse -Force
Copy-Item docs dist\AirLinker\docs -Recurse -Force
# Keep the exact modified receiver and host source with the local build.
New-Item -ItemType Directory -Force dist\AirLinker\source | Out-Null
Copy-Item airlinker,scripts,installer,vendor,tests,run.py,requirements.txt dist\AirLinker\source -Recurse -Force
Copy-Item scripts\configure-firewall.ps1 dist\AirLinker
& .venv\Scripts\python.exe scripts\collect-sources.py
if ($LASTEXITCODE) { throw "Source collection failed." }
& .\scripts\build-installer.ps1
