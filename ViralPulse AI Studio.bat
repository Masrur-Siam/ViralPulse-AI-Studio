@echo off
title ViralPulse AI Studio
cd /d "%~dp0"

set VIRALPULSE_NO_BROWSER=1
set PEAKCUT_NO_BROWSER=1

:: 1. Check if virtual environment python exists
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m studio.app
    goto :done
)

:: 2. Check if embedded/portable runtime python exists
if exist "runtime\python.exe" (
    "runtime\python.exe" -m studio.app
    goto :done
)

:: 3. Check if system python exists in PATH
where python >nul 2>nul
if %errorlevel% equ 0 (
    python -m studio.app
    goto :done
)

:: 4. If Python is not installed on this PC: auto-bootstrap portable Python
echo ================================================================
echo   ViralPulse AI Studio - Standalone Setup
echo   Python was not found on this computer.
echo   Setting up isolated portable runtime (one-time setup, ~25MB)...
echo ================================================================
echo.

if not exist "runtime" mkdir "runtime"
powershell -NoProfile -Command "Write-Host 'Downloading portable runtime...'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip' -OutFile 'runtime\python_embed.zip'; Expand-Archive -Path 'runtime\python_embed.zip' -DestinationPath 'runtime' -Force; Remove-Item 'runtime\python_embed.zip'"

if exist "runtime\python.exe" (
    echo Portable runtime ready! Launching ViralPulse AI Studio...
    "runtime\python.exe" -m studio.app
    goto :done
)

echo.
echo Failed to setup portable runtime automatically.
echo Please install Python 3.10+ from https://www.python.org/downloads/
pause

:done
