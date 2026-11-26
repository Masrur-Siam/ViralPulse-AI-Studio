"""Script to package ViralPulse AI Studio into a standalone .exe for distribution to PCs without Python."""
import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build():
    print("Building standalone ViralPulse AI Studio executable...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "ViralPulse AI Studio",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--icon", str(ROOT / "web" / "brand" / "app.ico"),
        "--add-data", f"{ROOT / 'web'};web",
        "--collect-all", "uvicorn",
        "--collect-all", "fastapi",
        "--collect-all", "starlette",
        "--collect-all", "webview",
        str(ROOT / "studio" / "app.py")
    ]
    res = subprocess.run(cmd, cwd=str(ROOT))
    if res.returncode == 0:
        print("Build SUCCESS! Standalone software folder created in dist/ViralPulse AI Studio/")
    else:
        print("Build failed with code:", res.returncode)


if __name__ == "__main__":
    build()
