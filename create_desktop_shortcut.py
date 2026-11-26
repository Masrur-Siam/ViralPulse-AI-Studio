import os
import sys
import subprocess
from pathlib import Path


def make_shortcut():
    root = Path(__file__).resolve().parent
    vbs_path = root / "ViralPulse AI Studio.vbs"
    ico_path = root / "web" / "brand" / "app.ico"
    candidates = [
        Path.home() / "OneDrive" / "Desktop",
        Path.home() / "Desktop",
    ]
    target_desktop = next((p for p in candidates if p.is_dir()), None)
    if not target_desktop:
        target_desktop = Path.home() / "Desktop"
        target_desktop.mkdir(parents=True, exist_ok=True)

    shortcut_path = target_desktop / "ViralPulse AI Studio.lnk"
    ps_script = f"""
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut('{str(shortcut_path)}')
    $Shortcut.TargetPath = '{str(vbs_path)}'
    $Shortcut.WorkingDirectory = '{str(root)}'
    $Shortcut.IconLocation = '{str(ico_path)},0'
    $Shortcut.Description = 'ViralPulse AI Studio - AI Video Clipping & Editing Software'
    $Shortcut.Save()
    """
    cmd = ["powershell", "-NoProfile", "-Command", ps_script]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if shortcut_path.is_file():
        print(f"SUCCESS: Created Desktop shortcut at {shortcut_path}")
        return True
    else:
        print("Failed to create shortcut:", res.stderr)
        return False


if __name__ == "__main__":
    make_shortcut()
