#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "====================================================================="
echo "             Starting ViralPulse AI Studio (macOS)..."
echo "====================================================================="

if [ ! -f ".venv/bin/python" ]; then
    echo "[!] Virtual environment not found. Running setup first..."
    ./setup_mac.command
    exit $?
fi

# Open browser on macOS
(sleep 1.5 && open "http://127.0.0.1:8765") &

exec .venv/bin/python -m studio.server
