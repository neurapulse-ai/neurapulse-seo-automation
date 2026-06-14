@echo off
title NeuraPulse Image Submission Bot
color 0A
cls

echo.
echo ============================================================
echo   NEURAPLUS IMAGE SUBMISSION BOT
echo   Automatic Backlink Builder for 96 Sites
echo ============================================================
echo.

REM ── STEP 1: Check Python ────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo   [!] Python not found. Installing now...
    curl -o "%TEMP%\python_installer.exe" https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    start /wait "%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1
    echo   Python installed!
)

REM ── STEP 2: Install packages ─────────────────────────────────
echo   [1/4] Checking packages...
python -m pip install selenium webdriver-manager pillow requests --quiet --upgrade
echo   Packages OK!
echo.

REM ── STEP 3: Create ALL missing folders and files ─────────────
echo   [2/4] Setting up folders and files...
if not exist "images"              mkdir "images"
if not exist "images\master"       mkdir "images\master"
if not exist "images\processed"    mkdir "images\processed"
if not exist "logs"                mkdir "logs"
if not exist "data"                mkdir "data"

REM Fix submission_log.json — write {} if missing or empty
if not exist "data\submission_log.json" (
    echo {} > "data\submission_log.json"
) else (
    for %%A in ("data\submission_log.json") do if %%~zA==0 echo {} > "data\submission_log.json"
)
echo   Folders and files OK!
echo.

REM ── STEP 4: Check image ──────────────────────────────────────
echo   [3/4] Checking for image...
if not exist "images\master\myimage.jpg" (
    echo.
    echo   ============================================================
    echo   IMAGE MISSING!
    echo   ============================================================
    echo   1. The images\master folder will now open
    echo   2. Copy YOUR image into that folder
    echo   3. Rename it to:  myimage.jpg
    echo   4. Double click START.bat again
    echo   ============================================================
    echo.
    explorer "images\master"
    pause
    exit
)
echo   Image found OK!
echo.

REM ── STEP 5: Run bot ──────────────────────────────────────────
echo   [4/4] Starting bot...
echo.
cd modules
python submitter.py
cd ..

echo.
echo ============================================================
echo   Done! Open dashboard.html in Chrome to see progress.
echo ============================================================
pause
