param(
    [ValidateSet('cu128', 'cpu')]
    [string]$Compute = 'cu128'
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonPath = Join-Path $ProjectRoot 'venv\Scripts\python.exe'

Push-Location -LiteralPath $ProjectRoot
try {
    if (-not (Test-Path -LiteralPath $PythonPath)) {
        & python -m venv venv
        if ($LASTEXITCODE -ne 0) { throw 'Could not create venv. Install Python 3.11 first.' }
    }

    # Install from the official PyTorch index so Windows gets CUDA wheels.
    & $PythonPath -m pip --cache-dir (Join-Path $ProjectRoot 'venv\pip-cache') install `
        "torch==2.9.1+$Compute" "torchvision==0.24.1+$Compute" `
        --index-url "https://download.pytorch.org/whl/$Compute"
    if ($LASTEXITCODE -ne 0) { throw 'PyTorch installation failed.' }

    & $PythonPath -m pip --cache-dir (Join-Path $ProjectRoot 'venv\pip-cache') install `
        --prefer-binary -r (Join-Path $ProjectRoot 'requirements-windows.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Learning dependency installation failed.' }

    & $PythonPath -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Dependency consistency check failed.' }

    $CheckArgs = @('-X', 'utf8', (Join-Path $PSScriptRoot 'check_learning_env.py'))
    if ($Compute -eq 'cu128') { $CheckArgs += '--require-cuda' }
    & $PythonPath @CheckArgs
    if ($LASTEXITCODE -ne 0) { throw 'Learning environment check failed.' }
}
finally {
    Pop-Location
}
