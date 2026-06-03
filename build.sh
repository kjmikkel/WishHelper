#!/usr/bin/env bash
# Build a standalone WishHelper executable (one-file, windowed) with PyInstaller.
# The embedded icon makes the OS task switcher use the WishHelper icon, because
# the running process is the WishHelper binary rather than the python launcher.
# (Icon embedding is Windows-centric; on macOS supply a .icns instead.)
set -euo pipefail

cd "$(dirname "$0")"

.venv/bin/python -m PyInstaller --noconfirm --clean --onefile --windowed \
    --name WishHelper \
    --icon "wishhelper/resources/wishlist.ico" \
    --collect-data wishhelper \
    --collect-all reportlab \
    "wishhelper/__main__.py"

echo
echo "Built dist/WishHelper"
