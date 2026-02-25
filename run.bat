@echo off
REM Port Scanner Launcher for Windows
REM This script installs dependencies and launches the application

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   Radar Port Scanner
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [✓] Python found
python --version

echo.
echo [*] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [✓] Dependencies installed

echo.
echo [*] Launching Port Scanner...
echo.

python main.py

endlocal
