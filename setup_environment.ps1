# CMIS3234 Shader Tutorial - Environment Setup Script (PowerShell)
# This script creates a virtual environment and installs all dependencies

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "   CMIS3234 Shader Programming - Environment Setup" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Check if Python is available
Write-Host "[1/4] Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host $pythonVersion -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found! Please install Python 3.10 or higher." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment already exists
if (Test-Path "shader_tutorial_venv") {
    Write-Host "`n[WARNING] Virtual environment already exists!" -ForegroundColor Yellow
    $recreate = Read-Host "Do you want to recreate it? (y/n)"
    if ($recreate -eq "y" -or $recreate -eq "Y") {
        Write-Host "[2/4] Removing old virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force shader_tutorial_venv
    } else {
        Write-Host "[2/4] Using existing virtual environment..." -ForegroundColor Green
        goto install_packages
    }
}

Write-Host "[2/4] Creating virtual environment..." -ForegroundColor Yellow
python -m venv shader_tutorial_venv

:install_packages
Write-Host "[3/4] Activating virtual environment..." -ForegroundColor Yellow
& ".\shader_tutorial_venv\Scripts\Activate.ps1"

Write-Host "[4/4] Installing required packages...`n" -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "   Setup Complete!" -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Green

Write-Host "To activate the virtual environment, run:" -ForegroundColor Cyan
Write-Host "   .\shader_tutorial_venv\Scripts\Activate.ps1  (PowerShell)" -ForegroundColor White
Write-Host "   shader_tutorial_venv\Scripts\activate.bat     (Command Prompt)`n" -ForegroundColor White

Write-Host "To verify installation, run:" -ForegroundColor Cyan
Write-Host "   python verify_environment.py`n" -ForegroundColor White

Write-Host "To start tutorials, run:" -ForegroundColor Cyan
Write-Host "   python run_tutorial.py`n" -ForegroundColor White

Write-Host "Or simply double-click: START_HERE.bat" -ForegroundColor Yellow
Write-Host "============================================================`n" -ForegroundColor Cyan

Read-Host "Press Enter to exit"
