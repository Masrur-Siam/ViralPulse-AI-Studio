@echo off
title ViralPulse AI Studio - Automated Setup
cd /d "%~dp0"

echo =====================================================================
echo                ViralPulse AI Studio - 1-Click Setup
echo                  Exclusively by Masrur Siam
echo =====================================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your system PATH!
    echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

:: 2. Create Python virtual environment if not present
if not exist ".venv\Scripts\python.exe" (
    echo [*] Creating virtual environment (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
)

:: 3. Install/upgrade dependencies
echo [*] Installing required packages from requirements.txt...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies failed to install. Continuing...
)

:: 4. Pre-download speech recognition model
echo [*] Checking speech recognition AI model...
".venv\Scripts\python.exe" -m studio.fetch_model

:: 5. Create Desktop shortcut
echo [*] Creating Windows Desktop shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_shortcut.ps1"

echo.
echo =====================================================================
echo             Setup Complete! Starting ViralPulse AI Studio...
echo =====================================================================
echo.

timeout /t 2 /nobreak >nul
call "%~dp0Launch_ViralPulse.bat"
