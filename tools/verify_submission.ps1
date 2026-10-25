param([Parameter(Mandatory = $true)][string]$PackagePath)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$package = (Resolve-Path -LiteralPath $PackagePath).Path
foreach ($relative in @('Application\DynamicSystemSimulator.exe', 'Application\_internal\python311.dll', 'Source-Code\src\dss\contracts.py', 'Source-Code\pyproject.toml', 'START_HERE.md', 'PACKAGED-ACCEPTANCE.json')) {
    $path = Join-Path $package $relative
    if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or (Get-Item -LiteralPath $path).Length -eq 0) {
        throw "Missing or empty submission file: $relative"
    }
}
$unwanted = @(Get-ChildItem -LiteralPath $package -Recurse -Force | Where-Object {
    $_.Name -in @('.venv', '.git', '__pycache__', '.pytest_cache') -or
    $_.Name -like '.env*' -or $_.Extension -in @('.pyc', '.pyo')
})
if ($unwanted.Count) { throw "Unwanted files in package: $($unwanted.FullName -join ', ')" }
$acceptance = Get-Content -LiteralPath (Join-Path $package 'PACKAGED-ACCEPTANCE.json') -Raw | ConvertFrom-Json
if (-not $acceptance.passed -or -not $acceptance.frozen -or $acceptance.cases.Count -ne 3) { throw 'Packaged acceptance is incomplete.' }
$shots = @(Get-ChildItem -LiteralPath (Join-Path $package 'Screenshots') -Recurse -File -Filter '*.png')
if ($shots.Count -lt 5) { throw 'At least five actual application screenshots are required.' }
Write-Host "PASS: staging folder integrity; $($shots.Count) screenshots; three frozen simulation cases."
$reports = @(Get-ChildItem -LiteralPath (Join-Path $package 'Final-Report') -File -Filter '*.pdf')
if (-not $reports.Count) { Write-Warning 'Final report missing: staging is usable but NOT submission-ready.' }
