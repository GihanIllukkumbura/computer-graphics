# Shader Programming Tutorials

A series of hands-on tutorials introducing modern OpenGL shader programming with Python.

## Quick Start

### 1. Setup Environment

```powershell
# From project root directory
python -m venv shader_tutorial_venv
.\shader_tutorial_venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run Tutorials

```powershell
cd tutorials

# Tutorial 01: Basic shaders and geometry
python 01_shader_intro.py

# Tutorial 02: Colors and varying values
python 02_shader_colors.py

# Tutorial 03: Fog effect with uniforms
python 03_shader_fog.py
```

## Tutorial Overview

### Tutorial 01: Shader Introduction

**File:** `01_shader_intro.py`  
**Topics:**

- Vertex and fragment shaders
- Vertex Buffer Objects (VBOs)
- Basic geometry rendering
- Green triangle and rectangle

**Output:** Green geometry on white background

---

### Tutorial 02: Shader Colors

**File:** `02_shader_colors.py`  
**Topics:**

- Varying values for shader communication
- Color interpolation across triangles
- Packed VBO data (position + color)
- Stride and offset usage
- Error handling

**Output:** Colorful geometry with smooth gradients

---

### Tutorial 03: Shader Fog

**File:** `03_shader_fog.py`  
**Topics:**

- Uniform values (CPU → GPU)
- Vertex shader calculations
- Distance-based fog effect
- Camera movement
- Interactive controls

**Output:** Geometry fading into fog

**Controls:**

- **Arrow Keys** - Move camera (forward/back/left/right)
- **PAGE UP/DOWN** - Move camera up/down
- **ESC** - Exit

---

## Teaching Guides

Detailed teaching guides with in-depth explanations are available in the `teaching_guides/` folder:

- `01_shader_intro_guide.md` - Comprehensive guide to Tutorial 01
- `02_shader_colors_guide.md` - Detailed explanation of interpolation
- `03_shader_fog_guide.md` - Uniforms and fog calculations

Each guide includes:

- Line-by-line code explanations
- Visual diagrams
- Common student questions
- Troubleshooting tips
- Experiment ideas
- Performance notes

---

## Requirements

- **Python:** 3.10 or higher
- **Packages:**
  - `pygame` - Window and event handling
  - `PyOpenGL` - OpenGL bindings
  - `PyOpenGL-accelerate` - Performance boost
  - `numpy` - Array operations

See `requirements.txt` for full details.

---

## Troubleshooting

### Module Not Found Error

```
ModuleNotFoundError: No module named 'OpenGL'
```

**Solution:** Make sure virtual environment is activated and packages are installed:

```powershell
.\shader_tutorial_venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Nothing Appears on Screen

- Verify shader compilation succeeded (check console output)
- Check that geometry is within camera view
- Ensure white background is working (geometry should contrast)

### Program Crashes Immediately

- Update graphics drivers
- Check Python version (3.10+ required)
- Try running without PyOpenGL-accelerate

---

## Learning Path

**Beginner:**

1. Complete Tutorial 01 - understand basic shader structure
2. Read the teaching guide to understand each line
3. Experiment with changing colors in fragment shader

**Intermediate:**

1. Complete Tutorial 02 - learn about varying values
2. Experiment with different color combinations
3. Try modifying vertex positions

**Advanced:**

1. Complete Tutorial 03 - master uniforms
2. Use arrow keys to explore fog interaction
3. Try implementing custom fog formulas
4. Experiment with different fog colors

---

## Next Steps

After completing these tutorials, you'll be ready to:

- Add texture mapping
- Implement lighting calculations
- Create custom material systems
- Build post-processing effects
- Develop advanced rendering techniques

---

## Credits

These tutorials are based on the OpenGLContext tutorial series, adapted to use Pygame for better cross-platform compatibility and modern Python practices.

**Course:** CMIS3234 - Computer Graphics  
**Topics:** Shader Programming with OpenGL and Python

---

## Additional Resources

- **GLSL Quick Reference:** `../GLSL_Quick_Reference.md`
- **Root Tutorial:** `../README_Shader_Tutorial.md`
- **PyOpenGL Documentation:** http://pyopengl.sourceforge.net/
- **Pygame Documentation:** https://www.pygame.org/docs/
