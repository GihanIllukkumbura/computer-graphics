# Simple Setup Guide

## 1. Create Virtual Environment

```powershell
python -m venv shader_tutorial_venv
```

## 1.1 Allow script execution

```powershell
Set-ExecutionPolicy RemoteSigned
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

## Tutorial Series

A comprehensive tutorial series is available in the [`tutorials/`](tutorials/) folder:

### Available Tutorials

1. **01_shader_intro.py** - Introduction to shaders and VBOs
2. **02_shader_colors.py** - Varying values and color interpolation
3. **03_shader_fog.py** - Uniform values and fog effects

Each tutorial includes:

- Working code with detailed comments
- Comprehensive teaching guide in `tutorials/teaching_guides/`
- Experiments to try
- Troubleshooting tips

**To run tutorials:**

```powershell
cd tutorials
python 01_shader_intro.py
```

See [`tutorials/README.md`](tutorials/README.md) for complete tutorial documentation.

---

**Done!** Your environment is ready to use.
