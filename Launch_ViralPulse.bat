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
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8765 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 1 /nobreak >nul

:: Open browser directly to ViralPulse Studio
start "" http://127.0.0.1:8765

:: Start ViralPulse Studio server (auto-terminates when browser is closed)
".venv\Scripts\python.exe" -m studio.server
exit
