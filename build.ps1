# Build a standalone WishHelper.exe (one-file, windowed) with PyInstaller.
# The embedded .ico makes the Windows taskbar show the WishHelper icon, because
# the running process is WishHelper.exe rather than python.exe.
$ErrorActionPreference = "Stop"
$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

# Push-Location so build/ and dist/ land in the repo root, without leaving the
# caller's working directory changed afterwards.
Push-Location $PSScriptRoot
try {
    & $py -m PyInstaller --noconfirm --clean --onefile --windowed `
        --name WishHelper `
        --icon "wishhelper\resources\wishlist.ico" `
        --collect-data wishhelper `
        --collect-all reportlab `
        "wishhelper\__main__.py"
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Built dist\WishHelper.exe"
