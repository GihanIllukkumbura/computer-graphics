# Tutorial 01: Shader Introduction

## What Are Shaders?

**Shaders** are small programs that run on your **GPU (Graphics Processing Unit)** rather than your CPU. They are written in specialized languages like **GLSL (OpenGL Shading Language)** and are responsible for determining how your 3D geometry appears on the screen.

### Why Are Shaders Important?

In modern graphics programming, shaders are essential because:

- They run in **parallel** on the GPU, processing thousands of vertices and pixels simultaneously
- They give you **complete control** over how objects are rendered
- They enable **advanced visual effects** like lighting, shadows, reflections, and post-processing
- They are the **modern way** to render graphics (fixed-function pipeline is deprecated)

### The Two Essential Shader Types

1. **Vertex Shader**
   - Runs **once per vertex** in your geometry
   - **Must produce**: `gl_Position` (the final screen position of the vertex)
   - Can also pass data to the fragment shader
   - Handles transformations (moving, rotating, scaling objects)

2. **Fragment Shader** (also called Pixel Shader)
   - Runs **once per pixel** being drawn to the screen
   - **Must produce**: `gl_FragColor` (the final color of the pixel)
   - Determines what color each pixel should be
   - Handles lighting calculations, texturing, and color effects

---

## Code Walkthrough: Line-by-Line Explanation

### 1. Imports Section

```python
import sys
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
from OpenGL.arrays import vbo
```

**Purpose**: Import necessary libraries

- `numpy`: For efficient numerical arrays (used to store vertex data)
- `pygame`: Provides window management and event handling
- `OpenGL.GL`: Core OpenGL functions for rendering
- `OpenGL.GLU`: OpenGL Utility library (for functions like `gluPerspective`)
- `shaders`: Module for compiling and managing shader programs
- `vbo`: Vertex Buffer Object support for storing geometry on GPU

---

### 2. TestContext Class Initialization

```python
class TestContext:
    """Creates a simple vertex shader..."""

    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.running = True
```

**Purpose**: Create a container class to manage the application

- Stores window dimensions (800x600 pixels)
- `self.running`: Flag to control the main loop

---

### 3. Display Initialization

```python
def init_display(self):
    """Initialize Pygame and OpenGL"""
    pygame.init()
    pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Tutorial 01: Shader Introduction")
```

**Purpose**: Set up the window and OpenGL context

- `pygame.init()`: Initialize all pygame modules
- `DOUBLEBUF`: Use double buffering (prevents flickering)
- `OPENGL`: Enable OpenGL rendering
- Sets the window title

```python
    # Set white background color
    glClearColor(1.0, 1.0, 1.0, 1.0)
```

**Purpose**: Define the background color

- `glClearColor(R, G, B, A)`: Sets clear color to white (1.0, 1.0, 1.0)
- Values range from 0.0 to 1.0

```python
    # Set up perspective projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (self.width / self.height), 0.1, 50.0)
```

**Purpose**: Configure the camera's perspective

- `GL_PROJECTION`: Switch to projection matrix (defines camera view)
- `glLoadIdentity()`: Reset matrix to identity (no transformation)
- `gluPerspective(FOV, aspect_ratio, near_clip, far_clip)`:
  - **45°** field of view
  - **Aspect ratio** based on window dimensions
  - **Near clip**: 0.1 units (minimum visible distance)
  - **Far clip**: 50.0 units (maximum visible distance)

```python
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # Move the camera back 10 units
    glTranslatef(0.0, 0.0, -10)
```

**Purpose**: Position the camera

- `GL_MODELVIEW`: Switch to model-view matrix (object transformations)
- Move camera back 10 units on Z-axis (so we can see objects at origin)

---

### 4. Shader Creation and Compilation

```python
def OnInit(self):
    """Initialize the context once we have a valid OpenGL environ"""

    # Vertex Shader
    VERTEX_SHADER = shaders.compileShader("""#version 120
    void main() {
        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    }""", GL_VERTEX_SHADER)
```

**Purpose**: Create and compile the vertex shader

- `#version 120`: GLSL version 1.20 (OpenGL 2.1)
- `void main()`: Entry point for the shader
- `gl_Vertex`: Input - the original vertex position
- `gl_ModelViewProjectionMatrix`: Transforms vertex from object space to screen space
- `gl_Position`: **Required output** - final position of the vertex

**What it does**: Takes each vertex and applies the model-view-projection transformation to convert it from 3D world coordinates to 2D screen coordinates.

```python
    # Fragment Shader
    FRAGMENT_SHADER = shaders.compileShader("""#version 120
    void main() {
        gl_FragColor = vec4( 0, 1, 0, 1 );
    }""", GL_FRAGMENT_SHADER)
```

**Purpose**: Create and compile the fragment shader

- `vec4(R, G, B, A)`: A 4-component vector (Red, Green, Blue, Alpha)
- `vec4(0, 1, 0, 1)`: Green color (no red, full green, no blue, full opacity)
- `gl_FragColor`: **Required output** - final color of the pixel

**What it does**: Makes every pixel solid green. This is the simplest possible fragment shader.

```python
    # Compile the shader program
    self.shader = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)
```

**Purpose**: Link the vertex and fragment shaders together

- A **shader program** is a complete rendering pipeline
- Both vertex and fragment shaders work together
- The program is stored in `self.shader` for later use

---

### 5. Vertex Buffer Object (VBO) Creation

```python
    # Create Vertex Buffer Object (VBO)
    self.vbo = vbo.VBO(
        np.array( [
            [  0, 1, 0 ],  # Triangle 1 - vertex 1
            [ -1,-1, 0 ],  # Triangle 1 - vertex 2
            [  1,-1, 0 ],  # Triangle 1 - vertex 3
            [  2,-1, 0 ],  # Triangle 2 - vertex 1
            [  4,-1, 0 ],  # Triangle 2 - vertex 2
            [  4, 1, 0 ],  # Triangle 2 - vertex 3
            [  2,-1, 0 ],  # Triangle 3 - vertex 1
            [  4, 1, 0 ],  # Triangle 3 - vertex 2
            [  2, 1, 0 ],  # Triangle 3 - vertex 3
        ], dtype='f')
    )
```

**Purpose**: Store vertex data on the GPU

**What is a VBO?**

- **Vertex Buffer Object** - a chunk of memory on the GPU
- Stores vertex data (positions, colors, normals, etc.)
- Much faster than sending data from CPU every frame

**The Geometry**:

- **9 vertices** total (each row is [X, Y, Z])
- **3 triangles** (3 vertices per triangle)
- **Triangle 1**: Forms a triangle pointing up on the left
- **Triangle 2 & 3**: Together form a square on the right

**Why `dtype='f'`?**

- `f` means 32-bit floating point numbers
- GPUs work best with this data type

**Visual representation**:

```
        (0,1)
         /\         (2,1)_____(4,1)
        /  \           |    /
    (-1,-1)(1,-1)      |  /
   Triangle 1          |/
                    (2,-1)__(4,-1)
                   Triangles 2&3
```

---

### 6. Render Function

```python
def Render(self):
    """Render the geometry for the scene."""

    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
```

**Purpose**: Clear previous frame

- `GL_COLOR_BUFFER_BIT`: Clear color information (uses `glClearColor`)
- `GL_DEPTH_BUFFER_BIT`: Clear depth buffer (for 3D depth testing)

```python
    # Tell OpenGL to use our compiled shader
    shaders.glUseProgram(self.shader)
```

**Purpose**: Activate our shader program

- From this point forward, our custom shaders handle rendering
- Without this, OpenGL would use the fixed-function pipeline (deprecated)

```python
    try:
        # Bind the VBO (make it active)
        self.vbo.bind()
```

**Purpose**: Make the VBO active

- Tells OpenGL "use this vertex data for the next draw call"

```python
        try:
            # Enable vertex array processing
            glEnableClientState(GL_VERTEX_ARRAY)
```

**Purpose**: Tell OpenGL we're providing vertex positions

- Enables the vertex position attribute

```python
            # Tell OpenGL where to find vertex data
            glVertexPointerf(self.vbo)
```

**Purpose**: Point OpenGL to our vertex data

- Connects the VBO data to the `gl_Vertex` variable in the vertex shader

```python
            # Draw the triangles (9 vertices = 3 triangles)
            glDrawArrays(GL_TRIANGLES, 0, 9)
```

**Purpose**: Actually render the geometry

- `GL_TRIANGLES`: Interpret every 3 vertices as a triangle
- `0`: Start at vertex index 0
- `9`: Use 9 vertices total

**What happens here**:

1. The vertex shader runs 9 times (once per vertex)
2. Each triangle is assembled from 3 transformed vertices
3. The fragment shader runs for every pixel inside each triangle
4. Each pixel becomes green

```python
        finally:
            # Clean up: unbind VBO and disable vertex array
            self.vbo.unbind()
            glDisableClientState(GL_VERTEX_ARRAY)
    finally:
        # Clean up: disable the shader
        shaders.glUseProgram(0)
```

**Purpose**: Clean up OpenGL state

- `finally` blocks ensure cleanup happens even if errors occur
- Unbind VBO (no longer using this data)
- Disable vertex array
- Disable shader (return to default state)
- Good practice to prevent state leaks

---

### 7. Event Handling

```python
def handle_events(self):
    """Handle Pygame events"""
    for event in pygame.event.get():
        if event.type == QUIT:
            self.running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.running = False
```

**Purpose**: Process user input

- Check for window close button
- Check for ESC key press
- Both set `self.running = False` to exit the main loop

---

### 8. Main Loop

```python
def main_loop(self):
    """Main application loop"""
    self.init_display()
    self.OnInit()

    clock = pygame.time.Clock()
```

**Purpose**: Set up and run the application

- Initialize display and OpenGL
- Create shaders and geometry
- Create a clock for frame rate limiting

```python
    while self.running:
        self.handle_events()
        self.Render()
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
```

**Purpose**: The game loop

1. **Handle events**: Process user input
2. **Render**: Draw the frame
3. **Flip**: Swap buffers (show the rendered frame)
4. **Tick**: Limit to 60 frames per second

**Why flip?**

- Double buffering: render to back buffer while front buffer displays
- Prevents tearing and flickering

```python
    pygame.quit()
```

**Purpose**: Clean shutdown when loop exits

---

## Summary: What This Code Does

1. **Creates a window** with OpenGL support
2. **Compiles shaders** that transform vertices and color pixels green
3. **Stores geometry** on the GPU (9 vertices forming 3 triangles)
4. **Renders** the triangles 60 times per second
5. **Handles input** to allow the user to exit

## Key Concepts Demonstrated

| Concept              | Why It Matters                          |
| -------------------- | --------------------------------------- |
| **Vertex Shader**    | Transforms 3D positions to screen space |
| **Fragment Shader**  | Determines pixel colors                 |
| **VBO**              | Efficient GPU storage for geometry      |
| **Shader Program**   | Links vertex and fragment shaders       |
| **Render Loop**      | Continuously updates the display        |
| **State Management** | Bind/unbind resources properly          |

## The Rendering Pipeline

```
Vertex Data (VBO)
    ↓
Vertex Shader (transform positions)
    ↓
Triangle Assembly (group vertices)
    ↓
Rasterization (find pixels inside triangles)
    ↓
Fragment Shader (color each pixel)
    ↓
Screen (final image)
```

## What You Should See

When you run this code, you'll see:

- **A white background** (from `glClearColor`)
- **A green triangle** on the left side
- **A green square** (made of 2 triangles) on the right side
- **All in solid green** because the fragment shader outputs `vec4(0, 1, 0, 1)`

## Next Steps

Future tutorials will show you how to:

- Pass colors from vertex shader to fragment shader
- Add lighting and shading
- Use textures
- Implement more complex transformations
- Add user interaction (rotation, zooming, etc.)

---

**Important**: This is the foundation of modern OpenGL programming. Understanding how shaders work and how to manage geometry on the GPU is essential for any graphics application.
