# Full Lecture Note - Tutorial 03 Shader Fog

Source file: `tutorials/03_shader_fog.py`

## 1. Lesson Goal
This file teaches how to send external values into shaders using uniforms, and how to produce distance-based fog by blending object color with a fog color.

Main learning idea:
- Tutorial 02 passed color with varyings.
- Tutorial 03 adds uniforms to control shader behavior from Python.

## 2. What This Program Demonstrates
The program shows:
- Uniform declaration and usage in GLSL
- Uniform location lookup in Python
- Uniform value upload each frame using `glUniform*`
- Fog intensity based on vertex depth in clip space
- Interactive camera movement to observe fog change

Visual result:
- Geometry appears to fade into white as distance increases
- User can move with keyboard and see fog response in real time

## 3. Program Flow (High-Level)
Execution order:
1. Program starts in `if __name__ == "__main__":`
2. Create `TestContext`
3. Run `main_loop()`
4. Initialize display and projection
5. Compile shader program and VBO in `OnInit()`
6. For each frame:
   - Process keyboard events
   - Set camera transform
   - Upload uniforms
   - Render geometry

## 4. Detailed Walkthrough by Function

### 4.1 `__init__(self, width=800, height=600)`
Stores window settings and runtime state.

Initial camera values:
- `camera_z = -10.0`
- `camera_x = 0.0`
- `camera_y = 0.0`

These values are later applied with `glTranslatef` every frame.

### 4.2 `init_display(self)`
Same base setup style as Tutorial 02:
- Create OpenGL window
- White clear color
- Perspective projection
- Initial backward translation so geometry is visible

White background is intentional because fog color is also white.

### 4.3 `OnInit(self)`
This function defines shader logic and lookup handles.

#### A. Vertex shader logic
Uniforms:
- `uniform float end_fog;`
- `uniform vec4 fog_color;`

Local variables:
- `fog_coord`: derived depth measure
- `fog`: blend factor for object color vs fog color

Key steps in shader:
1. `gl_Position = ftransform();`
2. `fog_coord = abs(gl_Position.z);`
3. `fog_coord = clamp(fog_coord, 0.0, end_fog);`
4. `fog = (end_fog - fog_coord)/end_fog;`
5. `fog = clamp(fog, 0.0, 1.0);`
6. `gl_FrontColor = mix(fog_color, gl_Color, fog);`

Interpretation:
- Near vertex -> fog close to 1 -> mostly original color
- Far vertex -> fog close to 0 -> mostly fog color

#### B. Fragment shader logic
Very simple:
- `gl_FragColor = gl_Color;`

Why simple:
- Fog blend already computed in vertex stage
- Interpolated final color arrives as `gl_Color`

#### C. Program and VBO
- Shader program compiled and linked
- Uses same packed position/color VBO format as Tutorial 02

#### D. Uniform location lookup
Code creates dictionary:
- `end_fog` location
- `fog_color` location

These integer-like handles are required for `glUniform*` calls.

### 4.4 `Render(self)`
Runs each frame and contains fog control path.

Frame steps:
1. Clear color + depth buffers
2. Reset model-view matrix
3. Apply camera translation from current input state
4. Activate shader program
5. Upload uniforms:
   - `glUniform1f(end_fog, 15)`
   - `glUniform4f(fog_color, 1,1,1,1)`
6. Apply extra transform:
   - rotate 45 degrees about Y axis
   - scale by 3 in all axes
7. Bind VBO and draw 9 vertices as triangles
8. Cleanup state and shader binding

Meaning of `end_fog = 15`:
- By depth 15 units, color is fully fogged.

### 4.5 `handle_events(self)`
Keyboard controls update camera position:
- `UP`: increase `camera_z` by 0.5 (move forward in this setup)
- `DOWN`: decrease `camera_z` by 0.5
- `LEFT`: increase `camera_x`
- `RIGHT`: decrease `camera_x`
- `PAGEUP`: decrease `camera_y`
- `PAGEDOWN`: increase `camera_y`
- `ESC`: exit

The effect of these controls is visible immediately because camera translation is reapplied every frame.

### 4.6 `main_loop(self)`
Lifecycle:
- One-time init
- Print controls
- Run update-render-present loop at 60 FPS
- Quit cleanly

## 5. Fog Math Used in This File
The implemented blend is equivalent to:

$$
f = clamp\left(\frac{end\_fog - d}{end\_fog}, 0, 1\right)
$$

where $d = |z|$ from transformed position.

Final vertex color:

$$
C_{out} = mix(C_{fog}, C_{vertex}, f)
$$

Equivalent expanded form:

$$
C_{out} = (1-f)C_{fog} + fC_{vertex}
$$

## 6. Important Design Decisions in This Code
1. Fog done in vertex shader:
   - Cheaper than fragment fog for many cases
   - Less precise than per-fragment fog, but simpler and faster
2. White fog + white clear color:
   - Gives natural fade into background
3. Using uniforms:
   - Easy to tune fog without recompiling shader

## 7. Common Student Confusions
1. Thinking uniforms are per-vertex values.
   Correction: uniform values are constant for the draw call.
2. Assuming fog should be computed from world-space position automatically.
   Correction: this file uses `gl_Position.z` after transform.
3. Thinking fragment shader must always perform advanced effects.
   Correction: many effects can be partially computed in vertex stage.

## 8. How Tutorial 03 Extends Tutorial 02
What is unchanged:
- VBO data layout
- Basic draw path
- Client state pointer setup

What is new:
- Uniform declarations
- Uniform location lookup
- `glUniform*` value uploads
- Fog blending math in shader
- Camera movement controls for interactive testing

## 9. Practical Summary
This file is a complete demonstration of controlled shader parameters (uniforms) and depth-based visual effects. Students should understand not only how to declare uniforms, but also how values travel from Python into GLSL and influence final color output in real time.
