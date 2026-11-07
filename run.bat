@echo off
title PharmaLit AI - Research Intelligence Platform
color 0B

echo ======================================================================
echo           PharmaLit AI - Literature Review Platform
echo ======================================================================
echo.

:: Check Python availability
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

:: Activate virtual environment if present
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment (.venv)...
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment (venv)...
    call venv\Scripts\activate.bat
)

echo [INFO] Starting PharmaLit AI locally at http://127.0.0.1:8501 ...
echo [INFO] Opening default browser...
start http://127.0.0.1:8501

python -m streamlit run app/main.py --server.port=8501 --server.address=127.0.0.1 --server.headless=true --browser.gatherUsageStats=false

pause
