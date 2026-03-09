@echo off
REM CMIS3234 Shader Tutorial - Environment Setup Script
REM This script creates a virtual environment and installs all dependencies

echo ============================================================
echo    CMIS3234 Shader Programming - Environment Setup
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.10 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Checking Python version...
python --version

REM Check if virtual environment already exists
if exist "shader_tutorial_venv" (
    echo.
    echo [WARNING] Virtual environment already exists!
    set /p RECREATE="Do you want to recreate it? (y/n): "
    if /i "%RECREATE%"=="y" (
        echo [2/4] Removing old virtual environment...
        rmdir /s /q shader_tutorial_venv
    ) else (
        echo [2/4] Using existing virtual environment...
        goto :install_packages
    )
)

echo [2/4] Creating virtual environment...
python -m venv shader_tutorial_venv

:install_packages
echo [3/4] Activating virtual environment...
call shader_tutorial_venv\Scripts\activate.bat

echo [4/4] Installing required packages...
echo.
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ============================================================
echo    Setup Complete!
echo ============================================================
echo.
echo To activate the virtual environment, run:
echo    shader_tutorial_venv\Scripts\activate.bat  (Command Prompt)
echo    shader_tutorial_venv\Scripts\Activate.ps1  (PowerShell)
echo.
echo To verify installation, run:
echo    python verify_environment.py
echo.
echo To start tutorials, run:
echo    python run_tutorial.py
echo.
echo Or simply double-click: START_HERE.bat
echo ============================================================
pause
