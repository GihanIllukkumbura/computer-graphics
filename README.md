# Simple Setup Guide

## 1. Create Virtual Environment

```powershell
python -m venv shader_tutorial_venv
```

## 2. Activate Virtual Environment

**PowerShell:**

```powershell
.\shader_tutorial_venv\Scripts\Activate.ps1
```

**Command Prompt:**

```cmd
shader_tutorial_venv\Scripts\activate.bat
```

## 3. Install Requirements

```powershell
pip install -r requirements.txt
```

## 4. Run Python Files

**Verify installation:**

```powershell
python verify_environment.py
```

**Run tutorials:**

```powershell
python shader_intro.py
```

```powershell
python shader_colors.py
```

**Or use the launcher:**

```powershell
python run_tutorial.py
```

## Quick Start (One Command)

```batch
setup_environment.bat
```

This automatically creates the venv, installs packages, and verifies the setup.

---

**Done!** Your environment is ready to use.
