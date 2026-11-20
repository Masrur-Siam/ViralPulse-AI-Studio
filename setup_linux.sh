#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "====================================================================="
echo "               ViralPulse AI Studio - Linux Setup"
echo "                 Exclusively by Masrur Siam"
echo "====================================================================="
echo ""

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.10+ (e.g. sudo apt install python3 python3-venv python3-pip ffmpeg)"
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

# Make launch script executable
chmod +x launch_linux.sh setup_linux.sh

# Create Desktop Entry
DESKTOP_DIR="$HOME/Desktop"
APPS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPS_DIR"

DESKTOP_FILE="$APPS_DIR/viralpulse.desktop"
cat > "$DESKTOP_FILE" << EOL
[Desktop Entry]
Version=1.0
Type=Application
Name=ViralPulse AI Studio
Comment=AI-Powered Viral Video Shorts Generator & Live Clipper
Exec=$DIR/launch_linux.sh
Icon=$DIR/web/brand/favicon.svg
Path=$DIR
Terminal=true
Categories=AudioVideo;Video;AudioVideoEditing;
EOL
chmod +x "$DESKTOP_FILE"

if [ -d "$DESKTOP_DIR" ]; then
    cp "$DESKTOP_FILE" "$DESKTOP_DIR/viralpulse.desktop"
    chmod +x "$DESKTOP_DIR/viralpulse.desktop"
    echo "[*] Desktop shortcut created on $DESKTOP_DIR/viralpulse.desktop"
fi

echo ""
echo "====================================================================="
echo "        Setup Complete! Launching ViralPulse AI Studio..."
echo "====================================================================="
echo ""

exec ./launch_linux.sh
