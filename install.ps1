# One-step installer: create the .venv and install WishHelper (+ dev deps) into
# it. Safe to re-run. Override the interpreter with $env:PYTHON.
$ErrorActionPreference = "Stop"

$python = if ($env:PYTHON) { $env:PYTHON } else { "python" }

& $python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Error ("WishHelper needs Python 3.12+. Found: {0}. " -f (& $python --version 2>&1) +
        "Set `$env:PYTHON to a 3.12+ interpreter and re-run.")
    exit 1
}

# Push-Location so `pip install -e .` runs against the repo root without leaving
# the caller's working directory changed afterwards.
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path ".venv")) {
        Write-Host "Creating virtual environment in .venv ..."
        & $python -m venv .venv
    }

    Write-Host "Installing WishHelper and dependencies ..."
    & .venv\Scripts\python.exe -m pip install --upgrade pip
    & .venv\Scripts\python.exe -m pip install -e ".[dev]"
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Done. Launch WishHelper with:  .\run.ps1"
