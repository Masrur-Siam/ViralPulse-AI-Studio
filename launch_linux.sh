#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "====================================================================="
echo "             Starting ViralPulse AI Studio (Linux)..."
echo "====================================================================="

if [ ! -f ".venv/bin/python" ]; then
    echo "[!] Virtual environment not found. Running setup first..."
    ./setup_linux.sh
    exit $?
fi

# Open default browser
if command -v xdg-open &> /dev/null; then
    (sleep 1.5 && xdg-open "http://127.0.0.1:8765") &
fi

exec .venv/bin/python -m studio.server
