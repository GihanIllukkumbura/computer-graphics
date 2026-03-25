# Tutorial 07: Multiple Lights, GLSL Arrays and Structures — Teaching Guide

## Overview
This tutorial extends our single-light renderer to handle **multiple lights** simultaneously. It introduces two key GLSL features: **structures** (to group material properties) and **arrays with looping** (to process multiple lights in one fragment shader).

**Based on**: OpenGLContext `shader_8.py`

---

## Prerequisites and Setup

Builds on Tutorial 06 (Specular/Blinn-Phong). Students should understand:
- Per-fragment Blinn-Phong lighting
- Uniforms, varyings, and attributes
- How `phong_weightCalc` returns diffuse + specular weights

---

## Learning Objectives

By the end of this tutorial, students will understand:
1. How to define and use **GLSL `struct`** types
2. How to declare and access **GLSL uniform arrays**
3. How to **loop** in GLSL to iterate over multiple lights
4. Why **array-of-structures** doesn't work for uniforms (practical limitation)
5. How `glUniform4fv` passes entire arrays to the GPU in one call
6. How the `w` component of position distinguishes directional vs point lights

---

## What's New in This Tutorial

Compared to Tutorial 06:
- ✅ **GLSL `struct Material`** replaces separate `Material_ambient`, `Material_diffuse`, etc.
- ✅ **`uniform vec4 lights[12]`** — flat array holds 3 lights × 4 vec4s each
- ✅ **`for` loop in fragment shader** — iterates over all lights
- ✅ **`glUniform4fv`** — uploads 12 vec4s in one call
- ✅ **Accumulative lighting** — each light's contribution is added to `fragColor`

---

## GLSL Structures

### Definition
```glsl
struct Material {
    vec4 ambient;
    vec4 diffuse;
    vec4 specular;
    float shininess;
};
```

### Rules
- Each field ends with `;`
- **No qualifiers** inside structs (no `uniform`, `in`, `out`)
- Must be defined **before** any variable uses it
- Accessed with dot notation: `material.ambient`, `material.diffuse`

### Declaring a Uniform of Struct Type
```glsl
uniform Material material;   // single Material instance
```

### Setting Struct Members from Python
```python
# Access each member individually:
glGetUniformLocation(shader, 'material.ambient')   # → valid location
glGetUniformLocation(shader, 'material.diffuse')    # → valid location
glGetUniformLocation(shader, 'material.shininess')  # → valid location
```

### Comparison: Before and After Structs

| Before (Tutorial 06) | After (Tutorial 07) |
|---|---|
| `uniform vec4 Material_ambient;` | `material.ambient` |
| `uniform vec4 Material_diffuse;` | `material.diffuse` |
| `uniform vec4 Material_specular;` | `material.specular` |
| `uniform float Material_shininess;` | `material.shininess` |

**Benefit**: Cleaner namespace, easier to have multiple materials (front/back).

---

## GLSL Arrays — Packing Multiple Lights

### The Problem
3 lights × 4 properties each = 12 separate uniforms. That's messy and doesn't scale.

### The Solution: Flat Array
```glsl
uniform vec4 lights[12];   // 3 lights × 4 vec4s each
```

**Memory layout:**
```
Index 0:  Light 0 — ambient   (vec4)
Index 1:  Light 0 — diffuse   (vec4)
Index 2:  Light 0 — specular  (vec4)
Index 3:  Light 0 — position  (vec4)
Index 4:  Light 1 — ambient   (vec4)
Index 5:  Light 1 — diffuse   (vec4)
Index 6:  Light 1 — specular  (vec4)
Index 7:  Light 1 — position  (vec4)
Index 8:  Light 2 — ambient   (vec4)
Index 9:  Light 2 — diffuse   (vec4)
Index 10: Light 2 — specular  (vec4)
Index 11: Light 2 — position  (vec4)
```

### Indexing with Constants
```glsl
int AMBIENT  = 0;
int DIFFUSE  = 1;
int SPECULAR = 2;
int POSITION = 3;

// For light i (stride of 4):
lights[i + AMBIENT]    // ambient of current light
lights[i + DIFFUSE]    // diffuse of current light
lights[i + SPECULAR]   // specular of current light
lights[i + POSITION]   // position of current light
```

---

## The Multi-Light Loop

```glsl
void main() {
    // Start with global ambient contribution
    vec4 fragColor = Global_ambient * material.ambient;

    int i;
    for (i = 0; i < 12; i = i + 4) {
        // Calculate light direction (eye-space)
        vec3 EC_Light_location = normalize(
            gl_NormalMatrix * lights[i + POSITION].xyz
        );
        // Half-vector for Blinn-Phong
        vec3 Light_half = normalize(
            EC_Light_location - vec3(0, 0, -1)
        );
        // Compute diffuse + specular weights
        vec2 weights = phong_weightCalc(
            EC_Light_location, Light_half,
            baseNormal, material.shininess
        );
        // ACCUMULATE this light's contribution
        fragColor = fragColor
            + (lights[i+AMBIENT]  * material.ambient)
            + (lights[i+DIFFUSE]  * material.diffuse  * weights.x)
            + (lights[i+SPECULAR] * material.specular  * weights.y);
    }
    gl_FragColor = fragColor;
}
```

**Key points:**
- Each light's contribution is **added** (accumulated)
- The loop increments by 4 (LIGHT_SIZE = 4 properties per light)
- `phong_weightCalc` is called once per light — same function from Tutorial 06

### Visual: Light Accumulation
```
Light 0 (red specular):   ○──→  ●  (red highlight right side)
Light 1 (green specular): ○──→  ●  (green highlight left side)
Light 2 (blue specular):  ○──→  ●  (blue highlight back)

Combined:  Three coloured specular highlights on sphere!
```

---

## Uploading the Light Array from Python

### The LIGHTS Array
```python
LIGHTS = array([
    # Light 0
    (.05,.05,.05,1.0),   # ambient
    (.3,.3,.3,1.0),      # diffuse
    (1.0,0.0,0.0,1.0),   # specular (RED)
    (4.0,2.0,10.0,0.0),  # position (w=0 → directional)
    # Light 1
    (.05,.05,.05,1.0),   # ambient
    (.3,.3,.3,1.0),      # diffuse
    (0.0,1.0,0.0,1.0),   # specular (GREEN)
    (-4.0,2.0,10.0,0.0), # position
    # Light 2
    (.05,.05,.05,1.0),   # ambient
    (.3,.3,.3,1.0),      # diffuse
    (0.0,0.0,1.0,1.0),   # specular (BLUE)
    (-4.0,2.0,-10.0,0.0),# position
], 'f')
```

### Uploading with `glUniform4fv`
```python
glUniform4fv(
    uniform_locations['lights'],
    12,           # number of vec4s (NOT number of lights!)
    self.LIGHTS
)
```

The **`v`** suffix means "vector" — pass an array of values. The count is the number of vec4 elements, not the number of lights.

---

## Why w=0.0 for Position?

```python
(4.0, 2.0, 10.0, 0.0)   # w = 0.0 → DIRECTIONAL light
(4.0, 2.0, 10.0, 1.0)   # w = 1.0 → POINT light (Tutorial 08)
```

A **directional light** (like the sun) has no position — only a direction. Setting `w=0.0` signals this. The `.xyz` is treated as a direction vector, not a position.

This convention comes from **homogeneous coordinates**:
- `w=1`: the vector represents a point in space
- `w=0`: the vector represents a direction (point at infinity)

---

## Why Not Array-of-Structures?

The tutorial explains an important **practical limitation**:

```glsl
// This COMPILES but DOESN'T WORK for setting uniforms:
struct LightSource {
    vec4 ambient;
    vec4 diffuse;
    vec4 specular;
    vec4 position;
};
uniform LightSource lights[3];
```

```python
# This always returns -1 (invalid):
glGetUniformLocation(shader, 'lights[0].ambient')
```

**Why?** GPU drivers don't properly implement array-of-struct uniform access. The built-in `gl_LightSource[i]` works because it's special-cased in the driver.

**Workaround:** Use a flat `vec4` array and index manually (as this tutorial does).

> [!WARNING]
> This is a real-world GPU driver limitation, not a GLSL specification issue. OpenGL 3.1+ Uniform Buffer Objects may resolve this.

---

## Exercises

### Exercise 1: Change Light Colours
Modify the `LIGHTS` array to create:
- Light 0: **yellow** specular `(1.0, 1.0, 0.0, 1.0)`
- Light 1: **cyan** specular `(0.0, 1.0, 1.0, 1.0)`
- Light 2: **magenta** specular `(1.0, 0.0, 1.0, 1.0)`

### Exercise 2: Add a 4th Light
Extend the system to support 4 lights:
1. Change `lights[12]` → `lights[16]` in the fragment shader
2. Change the loop: `for(i=0; i<16; i=i+4)`
3. Add a 4th light block to the `LIGHTS` array (4 more vec4s)
4. Change `glUniform4fv` count from 12 to 16

### Exercise 3: Dynamic Light Positions
Animate one light's position each frame:
```python
import math
angle = frame_count * 0.02
self.LIGHTS[3] = (  # Light 0 position (index 3)
    10 * math.cos(angle),
    2.0,
    10 * math.sin(angle),
    0.0
)
```

### Exercise 4: Trace the Accumulation
For a specific fragment normal `N = (0, 1, 0)`, manually calculate the contribution of each of the 3 lights and verify that the final colour is the sum.

### Exercise 5: Light Toggle
Add keyboard controls to enable/disable individual lights by setting their diffuse/specular to `(0,0,0,0)`.

---

## Common Student Questions

**Q: Why does the loop increment by 4 instead of 1?**
A: Each light occupies 4 consecutive vec4 elements in the flat array. Incrementing by 4 advances to the next light's block.

**Q: Can I use `for(int i=0; ...)` instead of declaring `i` separately?**
A: In GLSL 1.20, you must declare the iterator before the loop. From GLSL 1.30+, you can declare in the `for` statement.

**Q: What happens if I add too many lights? Will the shader get slow?**
A: Yes — each light adds more fragment shader operations. For N lights, each pixel does N × (1 normalize + 1 phong_weightCalc + 3 multiplies). 3 lights is fine; 100 lights would be very slow. Deferred rendering handles many lights more efficiently.

**Q: Can different lights have different types (directional vs point)?**
A: Not in this tutorial's code — all lights are treated as directional (the half-vector and light direction are computed the same way). Tutorial 08 adds point-light support by checking the `w` component.

---

## Key Takeaways

| Concept | What to Remember |
|---------|-----------------|
| **GLSL struct** | Group related uniforms; access with `struct.field` |
| **Uniform array** | `uniform vec4 lights[12]`; pass with `glUniform4fv` |
| **Multi-light loop** | Iterate with stride = LIGHT_SIZE; accumulate fragColor |
| **Array-of-struct** | Compiles but doesn't work for uniform access |
| **w=0 position** | Directional light (direction, not position) |

---

## What's Next

Tutorial 08 extends this to support **Point Light sources** — lights with an actual position in space (w=1.0) that fall off with distance (attenuation).
