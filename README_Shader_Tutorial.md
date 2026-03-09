# Shader-based OpenGL Programming for CMIS3234

This directory contains tutorials and examples for learning modern shader-based OpenGL programming using Python and GLSL (OpenGL Shading Language).

## Overview

These tutorials introduce modern, low-level 3D rendering techniques and avoid the use of "legacy" OpenGL entry points. Modern OpenGL uses **shaders** - small programs that run on the GPU to control rendering.

## Prerequisites

Students should have knowledge of:

- General programming with Python
- Some high school level mathematics (vectors, matrices)
- Basic understanding of 3D graphics concepts

## System Requirements

### Hardware

- Graphics card supporting OpenGL 2.0+ (most modern cards support OpenGL 3.0+)
- Note: Very old hardware may not work with these tutorials

### Software

- Windows 10/11 (these instructions are Windows-specific)
- Python 3.10 or higher

## Setup Instructions

### 1. Activate Virtual Environment

The virtual environment has already been created in this directory. To activate it:

```powershell
# Navigate to this directory
cd "E:\Z_PROJECTS\presentaion creation\computer graphics"

# Activate the virtual environment (Windows PowerShell)
.\shader_tutorial_venv\Scripts\Activate.ps1

# If you get a script execution error, run this once:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

For Command Prompt (cmd):

```cmd
shader_tutorial_venv\Scripts\activate.bat
```

### 2. Verify Installation

Check that required packages are installed:

```powershell
# With virtual environment activated
python -c "import OpenGL; print('PyOpenGL:', OpenGL.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import pygame; print('Pygame:', pygame.__version__)"
```

### 3. Run Your First Shader Program

```powershell
python shader_intro.py
```

You should see a window with a green triangle and square!

## Installed Packages

The virtual environment includes:

- **NumPy** (2.4.2) - Multi-dimensional arrays for passing data to OpenGL
- **PyOpenGL** (3.1.10) - Python bindings for OpenGL
- **PyOpenGL-accelerate** (3.1.10) - Performance optimizations
- **Pygame** (2.6.1) - Window management and event handling
- **PyGLM** (2.8.3) - OpenGL Mathematics library
- **Pillow** (12.1.1) - Image loading for textures

## Tutorial Structure

### Tutorial 1: shader_intro.py

**Introduction to Shaders - Basic Geometry**

Learn:

- What a vertex shader must do in GLSL
- What a fragment shader must do
- What a VBO (Vertex Buffer Object) looks like
- How to activate and deactivate shaders and VBOs
- How to render simple geometry

Key Concepts:

- **Vertex Shader**: Processes each vertex and calculates its position
- **Fragment Shader**: Determines the color of each pixel
- **VBO**: Efficient way to store vertex data on the GPU
- **GLSL**: OpenGL Shading Language - C-like syntax for shaders

## Important Terminology

### GLSL (OpenGL Shading Language)

The C-like language used to write shaders. There are two main types:

- **Vertex Shader**: Runs once per vertex
- **Fragment Shader**: Runs once per pixel/fragment

### Frustum

The viewing "stage" of your world - the part visible to the "camera". Includes:

- Near and far clipping planes
- Left, right, top, and bottom clipping planes

### Legacy OpenGL

Old OpenGL API that has been deprecated but is still widely supported. These tutorials use modern shader-based approaches instead.

### VBO (Vertex Buffer Object)

A buffer that stores vertex data directly on the GPU for efficient rendering.

## Coordinate Systems

OpenGL uses a right-handed coordinate system:

- X-axis: Left (-) to Right (+)
- Y-axis: Down (-) to Up (+)
- Z-axis: Into screen (-) to Out of screen (+)

## Shader Pipeline Overview

```
Vertex Data (CPU)
    ↓
VBO (GPU Memory)
    ↓
Vertex Shader (processes vertices)
    ↓
Primitive Assembly (forms triangles)
    ↓
Rasterization (generates fragments)
    ↓
Fragment Shader (colors pixels)
    ↓
Frame Buffer (display)
```

## Color Format in GLSL

Colors are specified as vec4(red, green, blue, alpha):

- Each component ranges from 0.0 to 1.0
- Example: vec4(1, 0, 0, 1) = opaque red
- Example: vec4(0, 1, 0, 1) = opaque green (used in tutorial)
- Example: vec4(0, 0, 1, 0.5) = semi-transparent blue

## Common Issues and Solutions

### Issue: "Script execution is disabled"

**Solution**: Run PowerShell as Administrator and execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: "OpenGL version not supported"

**Solution**: Update your graphics drivers from manufacturer's website (NVIDIA, AMD, or Intel)

### Issue: Black screen or no rendering

**Solution**:

1. Check console output for OpenGL errors
2. Verify your graphics card supports OpenGL 2.0+
3. Try updating graphics drivers

### Issue: Window closes immediately

**Solution**:

1. Run from terminal to see error messages
2. Check Python and package versions
3. Verify virtual environment is activated

## Learning Resources

### Official Documentation

- [PyOpenGL Documentation](http://pyopengl.sourceforge.net/)
- [OpenGL Reference Pages](https://www.khronos.org/registry/OpenGL-Refpages/)
- [GLSL Specification](https://www.khronos.org/opengl/wiki/OpenGL_Shading_Language)

### Original Tutorial Source

- [PyOpenGL Shader Tutorial](https://pyopengl.sourceforge.net/context/tutorials/shader_intro.html)

### Additional Learning

- [Learn OpenGL](https://learnopengl.com/) - Comprehensive modern OpenGL tutorial
- [OpenGL Tutorial](http://www.opengl-tutorial.org/) - Beginner-friendly tutorials

## Notes for Instructors

**Why Not OpenGLContext?**
The original tutorial uses OpenGLContext, which is no longer maintained and incompatible with Python 3.12+. This version uses Pygame instead, which is:

- Actively maintained
- Well-documented
- Widely used in education
- Compatible with modern Python

**Dependencies Not Installed:**

- OpenGLContext (obsolete, Python 2 syntax)
- PyVRML97 (dependency of OpenGLContext)
- TTFQuery (Python 2 syntax errors)
- simpleparse (build issues on modern Python)

These packages were required for the original tutorial framework but are not needed for learning shader programming concepts.

## Practice Exercises

### Exercise 1: Change Colors

Modify the fragment shader to render in different colors:

- Try making the geometry red
- Try making it blue
- Try making it partially transparent

### Exercise 2: Add More Geometry

Modify the VBO to add another triangle or square

### Exercise 3: Understanding Coordinates

Change the vertex positions and observe how the geometry changes

## Next Steps

After mastering this tutorial, students should explore:

1. Passing uniform variables to shaders
2. Using vertex attributes (colors, texture coordinates)
3. Multiple VBOs
4. Texture mapping
5. Lighting calculations in shaders
6. Matrix transformations

## Contact & Support

For questions about these tutorials, please contact your CMIS3234 instructor.

---

**Course**: CMIS3234  
**Topic**: Shader-based OpenGL Programming  
**Updated**: March 2026
