# Create a genuine RAR; a missing final report forces a clearly labeled staging archive.
param([Parameter(Mandatory = $true)][string]$PackagePath)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$package = (Resolve-Path -LiteralPath $PackagePath).Path
& (Join-Path $PSScriptRoot 'verify_submission.ps1') -PackagePath $package
$rar = Get-Command rar.exe -ErrorAction SilentlyContinue
$rarPath = if ($rar) { $rar.Source } else { Join-Path $env:ProgramFiles 'WinRAR\Rar.exe' }
if (-not (Test-Path -LiteralPath $rarPath)) {
    throw 'RAR creation unavailable: rar.exe not on PATH or in Program Files\WinRAR. The validated ZIP remains intermediate only.'
}
$reports = @(Get-ChildItem -LiteralPath (Join-Path $package 'Final-Report') -File -Filter '*.pdf')
$archiveName = if ($reports.Count) { 'CMPE443_Lab1_RaidynTeam_Final.rar' } else { 'CMPE443_Lab1_RaidynTeam_Staging.rar' }
$archive = Join-Path (Split-Path -Parent $package) $archiveName
if (Test-Path -LiteralPath $archive) {
    Move-Item -LiteralPath $archive -Destination ($archive + '.backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
}
Push-Location -LiteralPath (Split-Path -Parent $package)
try {
    & $rarPath a -r -idq $archive (Split-Path -Leaf $package)
    if ($LASTEXITCODE -ne 0) { throw 'RAR creation failed.' }
    & $rarPath t -idq $archive
    if ($LASTEXITCODE -ne 0) { throw 'RAR integrity test failed.' }
    $entries = @(& $rarPath lb $archive)
    if ($LASTEXITCODE -ne 0) { throw 'RAR contents could not be read.' }
    $parent = Split-Path -Parent $package
    foreach ($file in (Get-ChildItem -LiteralPath $package -Recurse -File)) {
        $relative = $file.FullName.Substring($parent.Length + 1)
        if ($relative -notin $entries) { throw "RAR entry missing: $relative" }
    }
    Write-Host "PASS: genuine RAR, integrity and every staged file verified: $archive"
    if (-not $reports.Count) { Write-Warning 'Approved report missing. RAR is staging only, NOT ready for Teams.' }
}
finally { Pop-Location }
