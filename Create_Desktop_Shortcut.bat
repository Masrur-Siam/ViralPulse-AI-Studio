@echo off
title Create Desktop Shortcut
cd /d "%~dp0"

echo Creating "ViralPulse AI Studio" shortcut on your Desktop...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_shortcut.ps1"

echo.
echo ====================================================================
echo  Success! The shortcut "ViralPulse AI Studio" is on your Desktop.
echo  You can now start the studio with just 1 double-click from Desktop!
echo ====================================================================
echo.
pause
