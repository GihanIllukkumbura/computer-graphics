# Shader Programming Quick Reference - CMIS3234

## GLSL Data Types

### Scalars

```glsl
float  myFloat = 1.0;     // 32-bit floating point
int    myInt = 1;         // 32-bit integer
bool   myBool = true;     // Boolean
```

### Vectors

```glsl
vec2   myVec2 = vec2(1.0, 2.0);           // 2D vector
vec3   myVec3 = vec3(1.0, 2.0, 3.0);      // 3D vector (RGB color, XYZ position)
vec4   myVec4 = vec4(1.0, 2.0, 3.0, 4.0); // 4D vector (RGBA, homogeneous coords)

// Vector swizzling (reordering components)
vec3 color = vec3(1.0, 0.5, 0.0);
vec3 bgr = color.bgr;        // Reverse order
vec2 rg = color.rg;          // First two components
vec4 rgba = vec4(color, 1.0); // Add alpha channel
```

### Matrices

```glsl
mat2   myMat2;  // 2x2 matrix
mat3   myMat3;  // 3x3 matrix
mat4   myMat4;  // 4x4 matrix (used for transformations)
```

## GLSL Variable Qualifiers

### attribute (vertex shader input)

```glsl
attribute vec3 vertexPosition;  // Per-vertex position data
attribute vec3 vertexColor;     // Per-vertex color data
attribute vec2 vertexTexCoord;  // Per-vertex texture coordinate
```

- Only available in vertex shader
- Different value for each vertex
- Read-only
- Provided by your application code

### varying (data passed between shaders)

```glsl
// In vertex shader (output)
varying vec3 fragmentColor;

// In fragment shader (input)
varying vec3 fragmentColor;
```

- Automatically interpolated across triangle
- Written in vertex shader, read in fragment shader
- Used to pass data that should be smoothly blended

### uniform (constant for all vertices/fragments)

```glsl
uniform float time;           // Animation time
uniform mat4 modelMatrix;     // Transformation matrix
uniform vec3 lightPosition;   // Light source position
```

- Same value for all vertices and fragments
- Read-only in shaders
- Set from application code
- Efficient for data that doesn't change per-vertex

## Built-in Variables

### Vertex Shader

```glsl
// Inputs (from fixed-function pipeline)
gl_Vertex              // vec4: vertex position
gl_Normal              // vec3: vertex normal
gl_Color               // vec4: vertex color
gl_MultiTexCoord0      // vec4: texture coordinate 0

// Built-in Matrices
gl_ModelViewMatrix               // mat4: model-view matrix
gl_ProjectionMatrix              // mat4: projection matrix
gl_ModelViewProjectionMatrix     // mat4: combined MVP matrix

// Required Output
gl_Position            // vec4: MUST SET - transformed vertex position
```

### Fragment Shader

```glsl
// Inputs
gl_FragCoord           // vec4: pixel coordinates (x, y, depth, 1/w)
gl_FrontFacing         // bool: true if front-facing

// Required Output
gl_FragColor           // vec4: MUST SET - final pixel color (RGBA)
```

## Common GLSL Functions

### Mathematical Functions

```glsl
sin(x), cos(x), tan(x)         // Trigonometry
abs(x)                         // Absolute value
min(x, y), max(x, y)           // Minimum, Maximum
clamp(x, min, max)             // Constrain to range
mix(x, y, a)                   // Linear interpolation: x*(1-a) + y*a
pow(x, y)                      // x raised to power y
sqrt(x)                        // Square root
```

### Vector Functions

```glsl
length(v)                      // Vector length/magnitude
distance(v1, v2)               // Distance between two points
dot(v1, v2)                    // Dot product
cross(v1, v2)                  // Cross product (vec3 only)
normalize(v)                   // Unit vector (length = 1)
reflect(I, N)                  // Reflection direction
```

### Color Functions

```glsl
vec3 color1 = vec3(1.0, 0.0, 0.0);  // Red
vec3 color2 = vec3(0.0, 1.0, 0.0);  // Green
vec3 mixed = mix(color1, color2, 0.5);  // Blend 50/50
```

## Python OpenGL Functions Reference

### Shader Compilation

```python
from OpenGL.GL import shaders

# Compile individual shaders
vertex_shader = shaders.compileShader(vertex_source, GL_VERTEX_SHADER)
fragment_shader = shaders.compileShader(fragment_source, GL_FRAGMENT_SHADER)

# Link into program
shader_program = shaders.compileProgram(vertex_shader, fragment_shader)

# Use shader
shaders.glUseProgram(shader_program)

# Stop using shader (return to fixed-function)
shaders.glUseProgram(0)
```

### VBO (Vertex Buffer Object)

```python
from OpenGL.arrays import vbo
import numpy as np

# Create VBO
vertices = np.array([
    [x, y, z],
    [x, y, z],
    # ... more vertices
], dtype='f')

my_vbo = vbo.VBO(vertices)

# Use VBO
my_vbo.bind()
glVertexPointer(3, GL_FLOAT, 0, None)
glDrawArrays(GL_TRIANGLES, 0, vertex_count)
my_vbo.unbind()
```

### Getting Shader Variable Locations

```python
# Get uniform location
time_location = glGetUniformLocation(shader_program, 'time')

# Get attribute location
color_location = glGetAttribLocation(shader_program, 'vertexColor')
```

### Setting Uniform Values

```python
# Float
glUniform1f(location, value)

# Vec3
glUniform3f(location, x, y, z)

# Vec4
glUniform4f(location, r, g, b, a)

# Matrix 4x4
glUniformMatrix4fv(location, 1, GL_FALSE, matrix_data)
```

### Drawing Commands

```python
# Draw arrays (sequential vertices)
glDrawArrays(GL_TRIANGLES, start_index, vertex_count)
glDrawArrays(GL_TRIANGLE_STRIP, start_index, vertex_count)
glDrawArrays(GL_POINTS, start_index, vertex_count)

# Draw elements (indexed vertices)
glDrawElements(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, indices)
```

## OpenGL Primitive Types

```python
GL_POINTS          # Individual points
GL_LINES           # Pairs of vertices form lines
GL_LINE_STRIP      # Connected line segments
GL_LINE_LOOP       # Connected line segments, closed loop
GL_TRIANGLES       # Triplets of vertices form triangles
GL_TRIANGLE_STRIP  # Connected triangles sharing edges
GL_TRIANGLE_FAN    # Triangles sharing a central vertex
```

## Color Values

### Common Colors (RGBA)

```glsl
vec4(1.0, 0.0, 0.0, 1.0)  // Red
vec4(0.0, 1.0, 0.0, 1.0)  // Green
vec4(0.0, 0.0, 1.0, 1.0)  // Blue
vec4(1.0, 1.0, 0.0, 1.0)  // Yellow
vec4(1.0, 0.0, 1.0, 1.0)  // Magenta
vec4(0.0, 1.0, 1.0, 1.0)  // Cyan
vec4(1.0, 1.0, 1.0, 1.0)  // White
vec4(0.0, 0.0, 0.0, 1.0)  // Black
vec4(0.5, 0.5, 0.5, 1.0)  // Gray
vec4(1.0, 0.5, 0.0, 1.0)  // Orange
```

### Alpha (Transparency)

- 0.0 = Fully transparent
- 0.5 = Half transparent
- 1.0 = Fully opaque

## Matrix Transformations

### Translation (Movement)

```glsl
mat4 translate = mat4(
    1.0, 0.0, 0.0, 0.0,
    0.0, 1.0, 0.0, 0.0,
    0.0, 0.0, 1.0, 0.0,
    tx,  ty,  tz,  1.0
);
```

### Scale

```glsl
mat4 scale = mat4(
    sx,  0.0, 0.0, 0.0,
    0.0, sy,  0.0, 0.0,
    0.0, 0.0, sz,  0.0,
    0.0, 0.0, 0.0, 1.0
);
```

### Common Matrix Operations

```glsl
// Apply transformation
vec4 transformedPosition = transformMatrix * originalPosition;

// Combine transformations (order matters!)
mat4 modelViewProjection = projection * view * model;
```

## Coordinate Systems

### Model Space

- Object's local coordinates
- Before any transformations

### World Space

- After model transformation
- Position in the "world"

### View Space (Camera Space)

- After view transformation
- Relative to camera

### Clip Space

- After projection transformation
- X, Y, Z in range [-1, 1]

### Screen Space

- After viewport transformation
- Actual pixel coordinates

## Common Shader Patterns

### Simple Color

```glsl
void main() {
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Red
}
```

### Interpolated Color

```glsl
// Vertex Shader
varying vec3 fragColor;
void main() {
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    fragColor = vertexColor;  // Pass to fragment shader
}

// Fragment Shader
varying vec3 fragColor;
void main() {
    gl_FragColor = vec4(fragColor, 1.0);
}
```

### Gradient Based on Position

```glsl
void main() {
    // Create horizontal gradient
    float intensity = gl_FragCoord.x / 800.0;  // Assuming 800px width
    gl_FragColor = vec4(intensity, 0.0, 1.0 - intensity, 1.0);
}
```

### Animated Color

```glsl
uniform float time;
void main() {
    float r = (sin(time) + 1.0) * 0.5;        // Oscillate between 0 and 1
    float g = (cos(time * 1.5) + 1.0) * 0.5;
    gl_FragColor = vec4(r, g, 0.5, 1.0);
}
```

## Common Errors and Solutions

### Error: "Shader compilation failed"

- Check for syntax errors in GLSL code
- Ensure all statements end with semicolon
- Check that main() is defined correctly
- Verify version directive (#version 120)

### Error: "Cannot find attribute/uniform"

- Variable name mismatch between shader and Python code
- Variable not used in shader (optimizer removes it)
- Shader not compiled successfully

### Problem: Black screen

- Check that gl_Position is set in vertex shader
- Check that gl_FragColor is set in fragment shader
- Verify shader is activated with glUseProgram()
- Check that VBO is bound before drawing

### Problem: Geometry not visible

- Check camera position (too close/far?)
- Verify vertex coordinates are reasonable
- Check depth testing settings
- Ensure correct primitive type (GL_TRIANGLES, etc.)

## Debugging Tips

1. **Start Simple**: Begin with solid colors before adding complexity
2. **Check Console**: Look for OpenGL/shader errors
3. **Test Incrementally**: Add one feature at a time
4. **Visualize Data**: Use colors to display values
5. **Check Ranges**: Ensure values are in expected ranges (0-1 for colors)

## Example: Complete Minimal Shader

### Vertex Shader

```glsl
#version 120
void main() {
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
```

### Fragment Shader

```glsl
#version 120
void main() {
    gl_FragColor = vec4(0.0, 1.0, 0.0, 1.0);  // Green
}
```

## Resources

- [GLSL Quick Reference](https://www.khronos.org/files/opengl-quick-reference-card.pdf)
- [PyOpenGL Documentation](http://pyopengl.sourceforge.net/)
- [OpenGL Reference Pages](https://www.khronos.org/registry/OpenGL-Refpages/)

---

**CMIS3234 - Computer Graphics**  
Keep this guide handy while working on shader tutorials!
