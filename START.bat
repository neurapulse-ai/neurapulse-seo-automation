@echo off
title IMAGE SUBMISSION BOT
color 0A
echo.
echo ============================================================
echo   IMAGE SUBMISSION BACKLINK BOT — Starting...
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo   Python not found. Installing Python...
    echo   Please download from https://www.python.org/downloads/
    echo   Make sure to check "Add Python to PATH" during install!
    pause
    exit
)

REM Install requirements if needed
echo   Checking required packages...
pip install selenium webdriver-manager pillow requests --quiet

echo.
echo   Starting bot...
echo.

REM Go to modules folder and run
cd /d "%~dp0modules"
python submitter.py

echo.
echo ============================================================
echo   Bot finished. Press any key to close.
echo ============================================================
pause
