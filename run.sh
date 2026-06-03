#!/usr/bin/env bash
# One-step launcher: run WishHelper via the .venv interpreter without activating
# it, so your shell session and working directory are left exactly as they were
# once the program exits. Installs first if the .venv is missing.
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
    echo "No virtual environment found. Running install.sh first ..."
    ./install.sh
fi

exec .venv/bin/python -m wishhelper "$@"
