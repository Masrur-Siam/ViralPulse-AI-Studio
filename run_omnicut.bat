@echo off
title OmniCut AI Studio
cd /d "%~dp0"

echo ========================================================
echo        Starting OmniCut AI Video Studio...
echo ========================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in .venv!
    pause
    exit /b 1
)

start "" http://127.0.0.1:8899
".venv\Scripts\python.exe" -m omnicut.main
pause
