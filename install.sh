#!/usr/bin/env bash
# One-step installer: create the .venv and install WishHelper (+ dev deps) into
# it. Safe to re-run. Override the interpreter with PYTHON=/path/to/python3.12.
set -euo pipefail

cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"

if ! "$PYTHON" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)'; then
    echo "WishHelper needs Python 3.12+. Found: $("$PYTHON" --version 2>&1)" >&2
    echo "Set PYTHON=/path/to/python3.12 and re-run." >&2
    exit 1
fi

if [ ! -d .venv ]; then
    echo "Creating virtual environment in .venv ..."
    "$PYTHON" -m venv .venv
fi

echo "Installing WishHelper and dependencies ..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"

echo
echo "Done. Launch WishHelper with:  ./run.sh"
