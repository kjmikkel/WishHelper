# One-step launcher: run WishHelper via the .venv interpreter without activating
# it. Deliberately avoids Set-Location (the PowerShell location is session-wide)
# so your shell and working directory are left exactly as they were on exit.
# Installs first if the .venv is missing.
$ErrorActionPreference = "Stop"

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "No virtual environment found. Running install.ps1 first ..."
    & (Join-Path $PSScriptRoot "install.ps1")
}

& $venvPython -m wishhelper @args
exit $LASTEXITCODE
