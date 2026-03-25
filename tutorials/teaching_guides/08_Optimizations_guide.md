# Tutorial 08: Optimizations for Directional Lights — Teaching Guide

## Overview

Fragment shaders are executed for every non-culled fragment (potential pixel) on the screen, meaning they run far more frequently than vertex shaders. Our previous implementation performed a lot of heavy light-vector calculations in the fragment shader. 

This short tutorial optimizes our renderer by **moving vertex-independent calculations** (such as determining the light half-vector and light location in eye-space) **from the fragment shader into the vertex shader**. We'll let the rasterizer interpolate these values for us.

**Based on:** OpenGLContext `shader_7.py` (Adapted for custom tutorial structure)

---

## Prerequisites and Setup

Builds on Tutorial 07 (Multiple Lights). Students should understand:
- The difference in execution frequency between vertex and fragment shaders.
- The concept of **varying** variables and how hardware interpolates them across a primitive.

---

## Learning Objectives

By the end of this tutorial, students will understand:
1. Why moving calculations from fragment to vertex shaders improves performance.
2. How to use **shared declaration blocks** to avoid duplicating GLSL code in Python.
3. How to interpolate arrays of vectors (`varying vec3 array[N]`) between shaders.

---

## Sharing Declarations

To keep our Python code clean and prevent mismatches between the vertex and fragment shaders, we can define a common string of GLSL declarations and prepend it to both shaders.

### The `lightConst` Block
```glsl
const int LIGHT_COUNT = 3;
const int LIGHT_SIZE = 4;
const int AMBIENT = 0;
const int DIFFUSE = 1;
const int SPECULAR = 2;
const int POSITION = 3;

uniform vec4 lights[ LIGHT_COUNT * LIGHT_SIZE ];

// New varying arrays to pass interpolated data to the fragment shader
varying vec3 EC_Light_half[LIGHT_COUNT];
varying vec3 EC_Light_location[LIGHT_COUNT];
varying vec3 baseNormal;
```
*Note that we dynamically insert `LIGHT_COUNT` and `LIGHT_SIZE` using Python string formatting (`%s`), allowing us to configure the shader from our Python script.*

---

## The Optimized Vertex Shader

We introduce a loop in the **vertex shader** to perform the heavy lifting of determining the light direction and the half-vector. 

```glsl
attribute vec3 Vertex_position;
attribute vec3 Vertex_normal;

void main() {
    gl_Position = gl_ModelViewProjectionMatrix * vec4(Vertex_position, 1.0);
    baseNormal = gl_NormalMatrix * normalize(Vertex_normal);
    
    // Pre-calculate light vectors per vertex instead of per fragment
    for (int i = 0; i < LIGHT_COUNT; i++) {
        EC_Light_location[i] = normalize(
            gl_NormalMatrix * lights[(i * LIGHT_SIZE) + POSITION].xyz
        );
        
        // half-vector calculation
        EC_Light_half[i] = normalize(
            EC_Light_location[i] - vec3(0, 0, -1)
        );
    }
}
```

By computing `EC_Light_location` and `EC_Light_half` at the vertex level, we take advantage of the hardware rasterizer to smoothly interpolate these vectors across the faces of our geometry.

---

## The Streamlined Fragment Shader

With the vectors already computed and interpolated, the loop in the **fragment shader** becomes much simpler and computationally cheaper:

```glsl
void main() {
    vec4 fragColor = Global_ambient * material.ambient;
    int i, j;
    
    for (i = 0; i < LIGHT_COUNT; i++) {
        j = i * LIGHT_SIZE;
        
        // Use the pre-calculated, interpolated varying values!
        vec2 weights = phong_weightCalc(
            EC_Light_location[i],
            EC_Light_half[i],
            baseNormal,
            material.shininess
        );
        
        fragColor = (
            fragColor
            + (lights[j+AMBIENT] * material.ambient)
            + (lights[j+DIFFUSE] * material.diffuse * weights.x)
            + (lights[j+SPECULAR] * material.specular * weights.y)
        );
    }
    gl_FragColor = fragColor;
}
```

### Why is this faster?
Imagine rendering a triangle that covers 1,000 pixels. 
- **Old way:** We perform the matrix multiplication and normalization for the light vectors 1,000 times (once per pixel).
- **New way:** We perform the matrix multiplication and normalization exactly 3 times (once per vertex). The rasterizer cheaply interpolates the results for the 1,000 pixels.

---

## Parameterized Array Uploads

Because we parameterized `LIGHT_COUNT` and `LIGHT_SIZE`, uploading the `lights` uniform array is now more robust:

```python
glUniform4fv(
    self.uniform_locations['lights'],
    self.LIGHT_COUNT * self.LIGHT_SIZE,  # Safely calculated total size!
    self.LIGHTS
)
```

---

## Key Takeaways

| Concept | What to Remember |
|---------|-----------------|
| **Vertex vs. Fragment Load** | Always look for calculations that can be shifted upstream to the vertex shader. Interpolation is fast; per-fragment computation is expensive. |
| **Shared GLSL code** | Injecting shared strings (like `lightConst`) prevents copy-paste errors and keeps constants synchronized across shader stages. |
| **Varying Arrays** | You can pass arrays of `varying` variables between shaders, which is perfect for processing multiple lights. |

---

## What's Next

With our shaders optimized, we now have the computational headroom to introduce more complex lighting models. In **Tutorial 09**, we will implement **Point Lights**, which have a defined position in space and attenuate (fall off) over distance.
