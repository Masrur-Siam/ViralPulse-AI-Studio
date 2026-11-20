#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "====================================================================="
echo "               ViralPulse AI Studio - macOS Setup"
echo "                 Exclusively by Masrur Siam"
echo "====================================================================="
echo ""

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.10+ (brew install python@3.11 ffmpeg)"
    read -p "Press Enter to exit..."
    exit 1
fi

# Create venv if not exists
if [ ! -f ".venv/bin/python" ]; then
    echo "[*] Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

# Install dependencies
echo "[*] Installing dependencies..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

# Fetch speech model
echo "[*] Fetching offline speech model..."
.venv/bin/python -m studio.fetch_model

# Make launch scripts executable
chmod +x "$DIR/launch_mac.command" "$DIR/setup_mac.command"

# Create Desktop Shortcut alias for macOS
DESKTOP_DIR="$HOME/Desktop"
if [ -d "$DESKTOP_DIR" ]; then
    ln -sf "$DIR/launch_mac.command" "$DESKTOP_DIR/ViralPulse AI Studio.command"
    echo "[*] Desktop launcher created at: $DESKTOP_DIR/ViralPulse AI Studio.command"
fi

echo ""
echo "====================================================================="
echo "        Setup Complete! Launching ViralPulse AI Studio..."
echo "====================================================================="
echo ""

exec "$DIR/launch_mac.command"
