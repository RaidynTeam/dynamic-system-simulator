# Build a portable (one-folder) Windows application and a Teams handoff ZIP.
# Run on Windows with Python 3.11: powershell -NoProfile -File tools/build_windows_submission.ps1
param([switch]$SkipTests, [switch]$SkipBuild)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $root
$python = Join-Path $root '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $python)) {
    & py -3.11 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 is required to create .venv.' }
}
$version = (& $python -c 'import sys; print(sys.version_info.major * 100 + sys.version_info.minor)')
if ($LASTEXITCODE -ne 0) {
    throw 'The existing .venv interpreter could not run the version check. Environment preserved; inspect the interpreter error above.'
}
if (([string]$version).Trim() -ne '311') {
    throw "Expected Python 3.11 in .venv; version code: $version. Environment preserved; use a separate Python 3.11 environment."
}

& $python -m pip install -r requirements.lock.txt
if ($LASTEXITCODE -ne 0) { throw 'Pinned runtime dependency install failed.' }
& $python -m pip install -e '.[dev]' 'pypdf==6.21.1' 'pyinstaller==6.22.3'
if ($LASTEXITCODE -ne 0) { throw 'Project / PyInstaller installation failed.' }
& $python -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Installed dependencies are inconsistent.' }

if (-not $SkipTests) {
    $oldQt = $env:QT_QPA_PLATFORM
    $oldMpl = $env:MPLBACKEND
    $env:QT_QPA_PLATFORM = 'offscreen'
    $env:MPLBACKEND = 'Agg'
    try {
        & $python -m pytest -q
        if ($LASTEXITCODE -ne 0) { throw 'Full test suite failed; no release should be submitted.' }
    }
    finally {
        if ($null -eq $oldQt) { Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue }
        else { $env:QT_QPA_PLATFORM = $oldQt }
        if ($null -eq $oldMpl) { Remove-Item Env:MPLBACKEND -ErrorAction SilentlyContinue }
        else { $env:MPLBACKEND = $oldMpl }
    }
    & $python tests/ui/native_smoke.py
    if ($LASTEXITCODE -ne 0) { throw 'Native UI smoke failed; no release should be submitted.' }
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
New-Item -ItemType Directory -Force -Path (Join-Path $root 'build') | Out-Null
if (-not $SkipBuild) {
    $buildPath = $env:PATH
    $basePython = & $python -c 'import sys; print(sys.base_prefix)'
    if ($LASTEXITCODE -ne 0) { throw 'Cannot resolve Python runtime directory.' }
    # External toolchains on PATH may contain incompatible ICU/UCRT DLLs. In
    # particular, Poppler ICU exports differ from Windows ICU used by Qt 6.12.
    $env:PATH = @((Split-Path -Parent $python), $basePython.Trim(), (Join-Path $env:SystemRoot 'System32'), $env:SystemRoot) -join ';'
    try {
        & $python -m PyInstaller --clean --noconfirm --onedir --windowed --specpath build `
            --name DynamicSystemSimulator --paths src `
            --collect-submodules dss `
            --exclude-module pytest --exclude-module tkinter --exclude-module IPython `
            --hidden-import matplotlib.backends.backend_qtagg `
            --hidden-import matplotlib.backends.backend_agg `
            --hidden-import matplotlib.backends.backend_pdf `
            tools/frozen_entry.py
        if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed.' }
    }
    finally { $env:PATH = $buildPath }
}
else { Write-Warning 'Reusing the existing frozen build. Only use -SkipBuild when application and frozen harness sources are unchanged.' }

$bundle = Join-Path $root 'dist\DynamicSystemSimulator'
$exe = Join-Path $bundle 'DynamicSystemSimulator.exe'
if (-not (Test-Path -LiteralPath $exe)) { throw 'The Windows EXE is missing after the build.' }
$qtPlugin = Get-ChildItem -LiteralPath $bundle -Recurse -Filter 'qwindows.dll' -File -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -eq $qtPlugin) { throw 'Qt Windows platform plugin qwindows.dll was not bundled.' }
& (Join-Path $PSScriptRoot 'verify_windows_exe.ps1') -ExePath $exe -OutputDirectory (Join-Path $root "build\acceptance-$stamp")

# A separate copy runs outside the checkout with Python import environment cleared.
# Retain this temporary evidence rather than deleting a computed directory.
$isolated = Join-Path ([IO.Path]::GetTempPath()) ('DSS-portable-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $isolated | Out-Null
Copy-Item -LiteralPath $bundle -Destination (Join-Path $isolated 'Application') -Recurse
& (Join-Path $PSScriptRoot 'verify_windows_exe.ps1') `
    -ExePath (Join-Path $isolated 'Application\DynamicSystemSimulator.exe') `
    -OutputDirectory (Join-Path $isolated 'Evidence')

$packageName = 'CMPE443_Lab1_RaidynTeam_Windows'
$package = Join-Path $root "dist\$packageName"
# Archive the entire previous staging folder before replacing generated files.
# Report and screenshots are copied forward; every other prior file remains in backup.
$previousPackage = $null
if (Test-Path -LiteralPath $package) {
    $previousPackage = "$package-backup-$stamp"
    $resolvedPackage = (Resolve-Path -LiteralPath $package).Path
    if ($resolvedPackage -ne (Join-Path $root "dist\$packageName")) { throw 'Unexpected staging path.' }
    Move-Item -LiteralPath $resolvedPackage -Destination $previousPackage
}
New-Item -ItemType Directory -Force -Path $package | Out-Null
$app = Join-Path $package 'Application'
$source = Join-Path $package 'Source-Code'
$report = Join-Path $package 'Final-Report'
$shots = Join-Path $package 'Screenshots'
foreach ($dir in @($app, $source, $report, $shots)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
Copy-Item -Path (Join-Path $bundle '*') -Destination $app -Recurse -Force
# Only tracked source/test/tool files plus this packaging implementation, never caches.
$sourceFiles = @(& git ls-files src tests tools .github docs/submission)
if ($LASTEXITCODE -ne 0) { throw 'Could not enumerate source files.' }
$sourceFiles += @(Get-ChildItem -LiteralPath $PSScriptRoot -File | ForEach-Object { 'tools/' + $_.Name })
$sourceFiles += @('.github/workflows/windows-portable.yml', 'docs/submission/WINDOWS-SUBMISSION.md')
foreach ($relative in ($sourceFiles | Sort-Object -Unique)) {
    $destination = Join-Path $source $relative
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
    Copy-Item -LiteralPath (Join-Path $root $relative) -Destination $destination
}
foreach ($file in @('README.md', 'LICENSE', 'pyproject.toml', 'requirements.txt', 'requirements.lock.txt', 'requirements-test.txt')) {
    $path = Join-Path $root $file
    if (Test-Path -LiteralPath $path) { Copy-Item -LiteralPath $path -Destination $source }
}
Copy-Item -LiteralPath (Join-Path $root 'docs\submission\WINDOWS-SUBMISSION.md') -Destination (Join-Path $package 'START_HERE.md')
if ($previousPackage) {
    foreach ($name in @('Final-Report', 'Screenshots')) {
        $prior = Join-Path $previousPackage $name
        if (Test-Path -LiteralPath $prior) {
            Get-ChildItem -LiteralPath $prior -Force | Copy-Item -Destination (Join-Path $package $name) -Recurse
        }
    }
}
$generatedShots = Join-Path $shots "Verified-$stamp"
New-Item -ItemType Directory -Path $generatedShots | Out-Null
Copy-Item -Path (Join-Path $isolated 'Evidence\case-*.png') -Destination $generatedShots
Copy-Item -LiteralPath (Join-Path $isolated 'Evidence\acceptance.json') -Destination (Join-Path $package 'PACKAGED-ACCEPTANCE.json')
if (-not (Get-ChildItem -LiteralPath $report -Filter '*.pdf' -File)) {
    'MISSING: Insert the actual team-approved final report PDF. The package is not submission-ready.' |
        Set-Content -LiteralPath (Join-Path $report 'MISSING_FINAL_REPORT.txt') -Encoding UTF8
}
& (Join-Path $PSScriptRoot 'verify_submission.ps1') -PackagePath $package

$zip = Join-Path $root "dist\$packageName.zip"
if (Test-Path -LiteralPath $zip) { Move-Item -LiteralPath $zip -Destination "$zip.backup-$stamp" }
Compress-Archive -LiteralPath $package -DestinationPath $zip -CompressionLevel Optimal
if (-not (Test-Path -LiteralPath $zip) -or (Get-Item -LiteralPath $zip).Length -le 0) { throw 'Portable ZIP was not created.' }
& $python (Join-Path $PSScriptRoot 'verify_submission_zip.py') $package $zip
if ($LASTEXITCODE -ne 0) { throw 'ZIP integrity verification failed.' }
Write-Host "PASS: Portable Windows EXE: $exe"
Write-Host "PASS: Submission staging folder: $package"
Write-Host "PASS: Staging ZIP: $zip"
Write-Host "PASS: Isolated application and acceptance evidence: $isolated"
Write-Host 'IMPORTANT: ZIP is intermediate. The real approved final PDF and a validated RAR are required for Teams.'
