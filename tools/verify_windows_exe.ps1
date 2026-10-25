# Validate files, a normal native window, and production-UI acceptance.
param(
    [Parameter(Mandatory = $true)][string]$ExePath,
    [string]$OutputDirectory,
    [int]$TimeoutSeconds = 180
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$exe = (Resolve-Path -LiteralPath $ExePath).Path
$bundle = Split-Path -Parent $exe
if ((Get-Item -LiteralPath $exe).Length -le 0) { throw 'Empty executable.' }
foreach ($pattern in @('qwindows.dll', 'python311.dll', 'Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll', 'vcruntime140.dll', '*openblas*.dll', 'DejaVuSans.ttf')) {
    if (-not (Get-ChildItem -LiteralPath $bundle -Recurse -File -Filter $pattern | Select-Object -First 1)) {
        throw "Missing bundled runtime component: $pattern"
    }
}
if (-not (Test-Path -LiteralPath (Join-Path $bundle '_internal\matplotlib\mpl-data'))) {
    throw 'Matplotlib data is missing.'
}
if (-not $OutputDirectory) { $OutputDirectory = Join-Path $bundle 'acceptance' }
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath (Join-Path $OutputDirectory 'acceptance.json')) {
    throw 'Use a fresh acceptance output directory to avoid stale evidence.'
}
$saved = @{}
foreach ($key in @('QT_QPA_PLATFORM', 'MPLBACKEND', 'PYTHONPATH', 'PYTHONHOME')) {
    $saved[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
    [Environment]::SetEnvironmentVariable($key, $null, 'Process')
}
$process = $null
try {
    # These are actual desktop acceptance runs; the window must be visible.
    $process = Start-Process -FilePath $exe -WorkingDirectory $bundle -WindowStyle Normal -PassThru
    $deadline = (Get-Date).AddSeconds(30)
    do {
        Start-Sleep -Milliseconds 200
        $process.Refresh()
        if ($process.HasExited) { throw "Normal GUI launch exited: $($process.ExitCode)" }
    } until ($process.MainWindowHandle -ne 0 -or (Get-Date) -gt $deadline)
    if ($process.MainWindowHandle -eq 0) { throw 'Process started but no native window initialized.' }
    if ($process.MainWindowTitle -notlike 'Dynamic System Simulator*') { throw "Unexpected startup window: $($process.MainWindowTitle)" }
    Write-Host "PASS: native window initialized: $($process.MainWindowTitle)"
    if (-not $process.CloseMainWindow()) { throw 'Could not request normal window closure.' }
    if (-not $process.WaitForExit(10000)) { throw 'Normal window closure timed out.' }
    if ($process.ExitCode -ne 0) { throw "Normal launch exit code: $($process.ExitCode)" }
    $process.Dispose()
    $process = Start-Process -FilePath $exe -WorkingDirectory $bundle -WindowStyle Normal -PassThru `
        -ArgumentList @('--acceptance-test', ('"' + $OutputDirectory + '"'))
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) { throw 'Frozen functional acceptance timed out.' }
    $resultPath = Join-Path $OutputDirectory 'acceptance.json'
    if (-not (Test-Path -LiteralPath $resultPath)) { throw "Acceptance produced no result; exit $($process.ExitCode)." }
    $result = Get-Content -LiteralPath $resultPath -Raw | ConvertFrom-Json
    if ($process.ExitCode -ne 0 -or -not $result.passed -or -not $result.frozen) {
        throw "Frozen acceptance failed: $(Get-Content -LiteralPath $resultPath -Raw)"
    }
    Write-Host "PASS: frozen native simulations, curves, metrics, dt/2, themes, repeat Run, PNG/PDF and close: $resultPath"
}
finally {
    if ($null -ne $process) {
        $process.Refresh()
        if (-not $process.HasExited) { Stop-Process -Id $process.Id -Force }
        $process.Dispose()
    }
    foreach ($key in $saved.Keys) { [Environment]::SetEnvironmentVariable($key, $saved[$key], 'Process') }
}
