@echo off
title Installing PharmaLit AI Dependencies
color 0A

echo ======================================================================
echo           PharmaLit AI - Automated Installation Script
echo ======================================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found in PATH!
    echo Please install Python 3.10, 3.11, or 3.12 and ensure "Add Python to PATH" is checked.
    pause
    exit /b 1
)

echo [1/3] Python detected:
python --version

:: Create virtual environment if requested or needed
if not exist ".venv" (
    echo [2/3] Creating Python virtual environment (.venv)...
    python -m venv .venv
)

echo [3/3] Installing dependencies from requirements.txt...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ======================================================================
echo    Installation Completed Successfully!
echo    Double-click run.bat to launch PharmaLit AI.
echo ======================================================================
pause
