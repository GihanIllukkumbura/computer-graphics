# Tutorial 01: Shader Introduction - Teaching Guide

## Overview

This is the first shader tutorial that introduces the fundamental concepts of modern OpenGL programming using shaders and Vertex Buffer Objects (VBOs).

---

## Prerequisites and Setup

### Required Software

- Python 3.10 or higher
- Virtual environment (recommended)

### Installation

1. **Create and activate virtual environment:**

```powershell
# Windows PowerShell
python -m venv shader_tutorial_venv
.\shader_tutorial_venv\Scripts\Activate.ps1
```

2. **Install required packages:**

```powershell
pip install -r requirements.txt
```

Required packages:

- `pygame>=2.6.0` - Window management and event handling
- `PyOpenGL>=3.1.7` - OpenGL bindings for Python
- `PyOpenGL-accelerate>=3.1.7` - Performance optimizations
- `numpy>=2.4.0` - Array operations

### Running the Tutorial

```powershell
cd tutorials
python 01_shader_intro.py
```

**Expected Output:** A window displaying a green triangle and rectangle on a white background.

---

## Learning Objectives

By the end of this tutorial, students will understand:

1. What a vertex shader does and what it MUST produce
2. What a fragment shader does and what it MUST produce
3. How to create and compile GLSL shaders
4. How to store geometry data in a VBO
5. How to render basic geometry using shaders

---

## Code Breakdown

### 1. Imports and Setup

```python
from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()
```

**What it does:**

- `OpenGLContext` is a library that provides cross-platform windowing
- `getInteractive()` chooses the best available window system (Pygame, wxPython, or GLUT)
- This allows the same code to run on different systems

```python
from OpenGL.GL import *
from OpenGL.arrays import vbo
from OpenGLContext.arrays import *
from OpenGL.GL import shaders
```

**What it does:**

- `OpenGL.GL` - Core OpenGL functions
- `vbo` - Vertex Buffer Object wrapper for easier use
- `arrays` - Array handling (uses Numpy)
- `shaders` - Convenience functions for shader compilation

---

### 2. Creating the Context Class

```python
class TestContext( BaseContext ):
    """Creates a simple vertex shader..."""
```

**What it does:**

- Inherits from `BaseContext` to create an OpenGL window
- All OpenGL rendering will happen within this class

---

### 3. Display Initialization

```python
def init_display(self):
    """Initialize Pygame and OpenGL"""
    pygame.init()
    pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Tutorial 01: Shader Introduction")

    # Set white background color
    glClearColor(1.0, 1.0, 1.0, 1.0)

    # Set up perspective projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (self.width / self.height), 0.1, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -10)
```

**Key Components:**

1. **pygame.init()** - Initialize Pygame subsystems
2. **pygame.display.set_mode()** - Create window with OpenGL support
   - `DOUBLEBUF` - Enable double buffering (smooth rendering)
   - `OPENGL` - Enable OpenGL rendering context

3. **glClearColor(1.0, 1.0, 1.0, 1.0)** - Set background to white
   - Parameters: (Red, Green, Blue, Alpha) all from 0.0 to 1.0
   - (1, 1, 1, 1) = opaque white
   - This creates a clean white canvas for our geometry

4. **Projection Setup:**
   - `gluPerspective(45, aspect, near, far)` - Creates 3D perspective
   - 45° field of view, aspect ratio, near=0.1, far=50.0

5. **Camera Position:**
   - `glTranslatef(0, 0, -10)` - Move camera back 10 units
   - Negative Z moves "away" from screen in OpenGL

**Why white background?**
In later tutorials (especially fog effects), having a white background allows geometry to naturally fade into the background color, creating realistic depth cues.

---

### 4. The OnInit Method

```python
def OnInit( self ):
    """Initialize the context once we have a valid OpenGL environ"""
```

**IMPORTANT:** This method is called AFTER OpenGL is ready. Never call OpenGL functions before this point or you'll get crashes!

---

### 4. Vertex Shader

```glsl
VERTEX_SHADER = shaders.compileShader("""#version 120
void main() {
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}""", GL_VERTEX_SHADER)
```

**Line-by-line explanation:**

- `#version 120` - Tells the GPU we're using GLSL version 1.20
- `void main()` - Entry point (like main() in C/C++)
- `gl_Position` - **REQUIRED OUTPUT** - This is what the vertex shader MUST set
- `gl_ModelViewProjectionMatrix` - Built-in matrix that transforms vertices from model space to screen space
- `gl_Vertex` - Built-in input containing the vertex position we passed in
- `*` - Matrix multiplication operator

**What it does:**

1. Takes each vertex position (gl_Vertex)
2. Multiplies it by the transformation matrix
3. Outputs the screen-space position (gl_Position)

**Key Concept - The Graphics Pipeline:**

```
Model Space → View Space → Clip Space → Screen Space
     ↑                ↑
   gl_Vertex    gl_Position
```

---

### 5. Fragment Shader

```glsl
FRAGMENT_SHADER = shaders.compileShader("""#version 120
void main() {
    gl_FragColor = vec4( 0, 1, 0, 1 );
}""", GL_FRAGMENT_SHADER)
```

**Line-by-line explanation:**

- `gl_FragColor` - **REQUIRED OUTPUT** - The color of this pixel
- `vec4( 0, 1, 0, 1 )` - RGBA color (Red=0, Green=1, Blue=0, Alpha=1)

**What it does:**

- Sets every pixel to pure green (0, 1, 0)
- Alpha=1 means fully opaque

**Key Concept - Fragments vs Pixels:**

- A "fragment" is a potential pixel
- Many fragments compete for the same pixel location
- The GPU decides which fragment "wins" based on depth

---

### 6. Compiling the Shader Program

```python
self.shader = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)
```

**What it does:**

1. Creates a shader program (glCreateProgram)
2. Attaches both shaders to it
3. Links them together (connects outputs of vertex shader to inputs of fragment shader)
4. Validates that everything is correct
5. Returns a reference number (handle) to use later

**Important:** Shaders must be compiled and linked before use!

---

### 7. Creating the VBO (Vertex Buffer Object)

```python
self.vbo = vbo.VBO(
    array( [
        [  0, 1, 0 ],  # Triangle 1 - vertex 1
        [ -1,-1, 0 ],  # Triangle 1 - vertex 2
        [  1,-1, 0 ],  # Triangle 1 - vertex 3
        [  2,-1, 0 ],  # Triangle 2 - vertex 1
        [  4,-1, 0 ],  # Triangle 2 - vertex 2
        [  4, 1, 0 ],  # Triangle 2 - vertex 3
        [  2,-1, 0 ],  # Triangle 3 - vertex 1
        [  4, 1, 0 ],  # Triangle 3 - vertex 2
        [  2, 1, 0 ],  # Triangle 3 - vertex 3
    ],'f')
)
```

**What it does:**

- Creates a buffer in GPU memory
- Stores vertex positions there
- `'f'` means 32-bit floating-point values

**Geometry Breakdown:**

```
Triangle 1: (0,1,0), (-1,-1,0), (1,-1,0)
   Makes a triangle pointing up

Triangles 2 & 3: Form a rectangle on the right
   They share vertices to connect together
```

**Why VBOs?**

- CPU → GPU data transfer is SLOW
- VBOs store data ON the GPU
- Much faster than sending data every frame

**Key Concept - Triangle Winding:**

```
     v1(0,1)
     /\
    /  \
   /____\
 v2(-1,-1) v3(1,-1)
```

Vertices are specified counter-clockwise (OpenGL default front-facing)

---

### 8. The Render Method

```python
def Render( self, mode):
    """Render the geometry for the scene."""
```

This method is called every frame to draw the scene.

---

### 9. Activating the Shader

```python
shaders.glUseProgram(self.shader)
```

**What it does:**

- Tells OpenGL: "Use THIS shader program for the next drawing commands"
- Without this, OpenGL uses the old fixed-function pipeline

---

### 10. Setting Up Vertex Data

```python
try:
    self.vbo.bind()
    try:
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointerf( self.vbo )
```

**Line-by-line:**

1. `self.vbo.bind()` - Makes this VBO "active"
2. `glEnableClientState(GL_VERTEX_ARRAY)` - Tells OpenGL: "I'm going to give you vertex positions"
3. `glVertexPointerf( self.vbo )` - Tells OpenGL: "Get vertex data from the active VBO"

**Why EnableClientState?**

- OpenGL has many types of vertex data (positions, colors, normals, etc.)
- You must enable each type you want to use
- This prevents accidental reading from uninitialized memory

---

### 11. Drawing the Geometry

```python
glDrawArrays(GL_TRIANGLES, 0, 9)
```

**Parameters:**

- `GL_TRIANGLES` - Draw mode: every 3 vertices make one triangle
- `0` - Start at vertex index 0
- `9` - Draw 9 vertices total (= 3 triangles)

**What happens:**

1. GPU reads 9 vertices from the VBO
2. Groups them into 3 triangles (vertices 0-2, 3-5, 6-8)
3. For each triangle:
   - Runs vertex shader 3 times (once per vertex)
   - Rasterizes the triangle into fragments
   - Runs fragment shader for each fragment
   - Writes final colors to the screen

**Timeline:**

```
Vertex Shader:    V1 V2 V3 V4 V5 V6 V7 V8 V9
                   ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓
Rasterization:   [Triangle 1] [Triangle 2] [Triangle 3]
                   ↓  ↓  ↓      ↓  ↓  ↓      ↓  ↓  ↓
Fragment Shader: F1 F2...Fn  F1 F2...Fn  F1 F2...Fn
```

---

### 12. Cleanup

```python
        finally:
            self.vbo.unbind()
            glDisableClientState(GL_VERTEX_ARRAY)
    finally:
        shaders.glUseProgram( 0 )
```

**What it does:**

- `unbind()` - Deactivate the VBO
- `glDisableClientState()` - Turn off vertex array processing
- `glUseProgram(0)` - Deactivate the shader

**Why cleanup?**

- Other code might not expect these things to be active
- Prevents state leakage between different rendering operations
- Good practice for debugging

**The try-finally pattern:**

- Ensures cleanup happens even if an error occurs
- Nested try blocks clean up in reverse order

---

### 13. Running the Program

```python
if __name__ == "__main__":
    TestContext.ContextMainLoop()
```

**What it does:**

- `if __name__ == "__main__"` - Only runs if this file is executed directly
- `ContextMainLoop()` - Opens window and starts the render loop

**The Main Loop does:**

1. Handle window events (close, resize, etc.)
2. Call `Render()` method
3. Swap buffers (display the rendered frame)
4. Repeat until window closes

---

## Key Concepts Summary

### 1. The Graphics Pipeline

```
CPU → VBO (GPU Memory) → Vertex Shader → Rasterization → Fragment Shader → Screen
```

### 2. Shader Requirements

- **Vertex Shader MUST set:** `gl_Position` (vec4)
- **Fragment Shader MUST set:** `gl_FragColor` (vec4)

### 3. VBO Benefits

- Stores data on GPU (fast)
- Reduces CPU→GPU bandwidth
- Required for modern OpenGL

### 4. The Render Cycle

1. Activate shader
2. Bind VBO
3. Enable arrays
4. Set pointers
5. Draw
6. Cleanup

---

## Common Student Questions

**Q: Why do we need shaders? Can't we just draw triangles?**
A: Modern GPUs require shaders. The old "fixed-function pipeline" is deprecated. Shaders give you complete control over how geometry is transformed and colored.

**Q: What's the difference between a vertex and a fragment?**
A: A vertex is a corner of a triangle. A fragment is a potential pixel. One triangle (3 vertices) creates hundreds or thousands of fragments.

**Q: Why is everything green?**
A: Our fragment shader returns `vec4(0, 1, 0, 1)` for every pixel, which is green. In the next tutorial, we'll make each vertex a different color.

**Q: What is gl_ModelViewProjectionMatrix?**
A: It's a built-in matrix that transforms vertices from model space (where you define your geometry) to clip space (where the GPU can clip and rasterize it). It combines three transformations: Model → View → Projection.

**Q: Can I see the triangles rotate?**
A: Not yet. The geometry is static. Later tutorials will show how to animate by changing the transformation matrix each frame.

**Q: Why use try-finally for cleanup?**
A: If an error occurs during rendering, the finally block ensures we still clean up. Otherwise, OpenGL state can get corrupted and cause strange errors later.

---

## Experiments to Try

1. **Change the color:** Modify the fragment shader to output different colors
   - Red: `vec4(1, 0, 0, 1)`
   - Blue: `vec4(0, 0, 1, 1)`
   - Half-transparent white: `vec4(1, 1, 1, 0.5)`

2. **Modify vertex positions:** Change the VBO coordinates to create different shapes
   - Try making a larger triangle
   - Try adding more triangles (remember to update the count in glDrawArrays)

3. **Break it intentionally:**
   - Remove `gl_Position =` line from vertex shader → compile error
   - Remove `gl_FragColor =` line from fragment shader → compile error
   - Change `9` to `3` in glDrawArrays → only draws 1 triangle
   - Comment out `glEnableClientState` → nothing draws

4. **Add more geometry:** Add more vertices to create additional triangles

---

## Troubleshooting

**Nothing appears on screen:**

- Check that shader compiled without errors
- Verify VBO has correct data
- Ensure glDrawArrays count matches number of vertices
- Make sure cleanup code doesn't run before drawing

**Green screen with no geometry:**

- Your fragment shader is running but geometry isn't being processed
- Check vertex shader syntax
- Verify glEnableClientState was called

**Program crashes:**

- Don't call OpenGL functions before OnInit
- Make sure window system (Pygame/GLUT) is installed
- Check that cleanup (unbind, disable) is properly done

---

## Next Steps

In Tutorial 02, we'll learn:

- How to add colors to each vertex
- Using "varying" values to pass data between shaders
- How the GPU interpolates values across triangles
- Packing multiple data types into one VBO

---

## Additional Resources

**GLSL Reference:**

- See `GLSL_Quick_Reference.md` in the project root

**OpenGL Pipeline:**

```text
  Application (Python)
        ↓
  Vertex Specification (VBO setup)
        ↓
  Vertex Shader ← Uniforms & Attributes
        ↓
  Primitive Assembly (form triangles)
        ↓
  Rasterization (create fragments)
        ↓
  Fragment Shader ← Uniforms & Varyings
        ↓
  Framebuffer (screen)
```

**Key Terms:**

- **Vertex:** A point in 3D space (has position, and optionally color, normal, etc.)
- **Fragment:** A potential pixel generated during rasterization
- **Shader:** A program that runs on the GPU
- **VBO:** Vertex Buffer Object - memory on the GPU storing vertex data
- **Pipeline:** The sequence of steps from vertex data to final pixels
- **GLSL:** OpenGL Shading Language - C-like language for writing shaders
