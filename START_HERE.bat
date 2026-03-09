@echo off
REM Quick launcher for CMIS3234 Shader Tutorials
REM Double-click this file to start!

echo ========================================================
echo    CMIS3234 - Shader Programming Tutorial Launcher
echo ========================================================
echo.

REM Check if virtual environment exists
if not exist "shader_tutorial_venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please make sure you're in the correct directory:
    echo E:\Z_PROJECTS\presentaion creation\computer graphics
    echo.
    pause
    exit /b 1
)

echo [OK] Virtual environment found
echo.

REM Activate virtual environment and run tutorial launcher
call shader_tutorial_venv\Scripts\activate.bat

echo.
echo Starting tutorial launcher...
echo.

python run_tutorial.py

REM Deactivate on exit
call shader_tutorial_venv\Scripts\deactivate.bat

pause
