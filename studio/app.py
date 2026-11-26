"""ViralPulse AI Studio - Desktop Application Launcher.
Runs the studio in a native window with hardware acceleration, system tray, and local network sharing.
"""
import os
import sys

# Prevent server from auto-launching external browser so only the app window opens
os.environ["VIRALPULSE_NO_BROWSER"] = "1"
os.environ["PEAKCUT_NO_BROWSER"] = "1"

import time
import socket
import shutil
import urllib.request
import threading
import subprocess
import webbrowser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from studio import config, server


def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def run_server():
    import uvicorn
    host = os.environ.get("PEAKCUT_HOST", "0.0.0.0")
    port = int(os.environ.get("PEAKCUT_PORT", config.PORT or 8765))
    uvicorn.run(server.app, host=host, port=port, log_level="warning", access_log=False)


def wait_for_server(port, timeout=12.0):
    start = time.time()
    url = f"http://127.0.0.1:{port}/api/status"
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.2)
    return False


def find_browser_app_mode():
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        shutil.which("msedge"),
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("brave"),
    ]
    for b in candidates:
        if b and os.path.isfile(b):
            return b
    return None


def main():
    port = int(os.environ.get("PEAKCUT_PORT", config.PORT or 8765))
    lan_ip = get_lan_ip()
    print("=" * 60)
    print("  🚀 ViralPulse AI Studio - Standalone Desktop Software")
    print(f"  • Local Application: http://127.0.0.1:{port}")
    print(f"  • Open on Phone / Tablet / other devices: http://{lan_ip}:{port}")
    print("=" * 60)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    ready = wait_for_server(port, timeout=12.0)
    if not ready:
        print("Warning: Server took longer than expected to start.")

    app_url = f"http://127.0.0.1:{port}"
    icon_path = ROOT_DIR / "web" / "brand" / "app.ico"

    # Strategy 1: PyWebView Native Window
    try:
        import webview
        window = webview.create_window(
            title="ViralPulse AI Studio",
            url=app_url,
            width=1320,
            height=860,
            min_size=(960, 640),
            text_select=True,
            zoomable=True
        )
        webview.start(icon=str(icon_path) if icon_path.is_file() else None)
        print("Closing ViralPulse AI Studio...")
        os._exit(0)
    except Exception as e:
        print(f"pywebview window could not start ({e}), falling back to native app mode...")

    # Strategy 2: Edge / Chrome Standalone App Window (Frameless with no URL bar)
    browser_bin = find_browser_app_mode()
    if browser_bin:
        try:
            cmd = [browser_bin, f"--app={app_url}", "--window-size=1320,860"]
            proc = subprocess.Popen(cmd)
            proc.wait()
            print("Closing ViralPulse AI Studio...")
            os._exit(0)
        except Exception:
            pass

    # Strategy 3: Default Browser Fallback
    webbrowser.open(app_url)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        os._exit(0)


if __name__ == "__main__":
    main()
