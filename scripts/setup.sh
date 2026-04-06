#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
USE_VENV=0

if [[ "${1:-}" == "--venv" ]]; then
	USE_VENV=1
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
	echo "Could not find $PYTHON_BIN on PATH." >&2
	exit 1
fi

if [[ "$USE_VENV" -eq 1 ]]; then
	"$PYTHON_BIN" -m venv .venv
	source .venv/bin/activate
	python -m pip install --upgrade pip
	python -m pip install -r requirements-dev.txt

	echo "Environment ready (.venv)."
	echo "Activate with: source .venv/bin/activate"
	exit 0
fi

"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install --user -r requirements-dev.txt

echo "Environment ready (user-site install)."
echo "Run Navil with: $PYTHON_BIN -m navil"
echo "Optional isolated mode: ./scripts/setup.sh --venv"
