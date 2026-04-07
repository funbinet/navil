#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ "${1:-}" == "--venv" ]]; then
	echo "Virtual environments are intentionally disabled for this repository." >&2
	echo "Run ./scripts/setup.sh with system Python only." >&2
	exit 1
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
	echo "Could not find $PYTHON_BIN on PATH." >&2
	exit 1
fi

if ! "$PYTHON_BIN" -m pip install --upgrade pip; then
	echo "Retrying pip upgrade with --break-system-packages" >&2
	"$PYTHON_BIN" -m pip install --break-system-packages --upgrade pip
fi
if ! "$PYTHON_BIN" -m pip install --user -r requirements-dev.txt; then
	echo "Retrying dependency install with --break-system-packages" >&2
	"$PYTHON_BIN" -m pip install --user --break-system-packages -r requirements-dev.txt
fi

if ! "$PYTHON_BIN" -m pip install --user -e .; then
	echo "Retrying project install with --break-system-packages" >&2
	"$PYTHON_BIN" -m pip install --user --break-system-packages -e .
fi

echo "Environment ready (user-site install)."
echo "Run Navil with: $PYTHON_BIN -m navil"
echo "Command mode: navil or navel"
echo "If command is missing, add user bin to PATH: export PATH=\"$HOME/.local/bin:$PATH\""
