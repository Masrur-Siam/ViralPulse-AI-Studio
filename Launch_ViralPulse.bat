@echo off
title ViralPulse AI Studio
cd /d "%~dp0"

echo ========================================================
echo             Starting ViralPulse AI Studio...
echo       Next-Gen AI Viral Shorts & Engagement Engine
echo ========================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [*] First time launch detected. Automatically configuring environment...
    call "%~dp0Setup_Windows.bat"
    exit /b
)

:: Automatically close any old instance holding port 8765
for /f "tokens=5" %%a in ('netstat -aon ^| findstr /i :8765') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo [*] Launching Studio Engine...
echo [*] Browser will open automatically once the engine is ready.
echo.

:: Start ViralPulse Studio server (browser opens automatically as soon as port is ready)
".venv\Scripts\python.exe" -m studio.server
exit
