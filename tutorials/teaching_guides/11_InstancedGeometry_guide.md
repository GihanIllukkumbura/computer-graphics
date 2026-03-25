# Tutorial 11: Instanced Geometry and Texture Buffer Extensions — Teaching Guide

## Overview
As our rendering scenarios expand, drawing thousands of spheres using singular draw calls via CPU iteration becomes very detrimental to performance. This tutorial uses the `ARB_draw_instanced` and `ARB_texture_buffer_object` extensions to drastically boost performance by drawing many parameterized copies of a single mesh with one function call.

**Based on:** OpenGLContext `shader_instanced.py`

---

## Prerequisites and Setup
Builds on Tutorial 10 (Spot Lights). Students should understand:
- The `GLSLShader` mechanism and handling multiple objects.
- How memory sizes define arrays and bounds limits in VBOs.

---

## Learning Objectives
By the end of this tutorial, students will understand:
1. The difference between `glDrawElements` and `glDrawElementsInstanced`.
2. How to use `gl_InstanceIDARB` inside a vertex shader.
3. How to create `TextureBufferObject` arrays to supply a unique property (like an offset or rotation) per instantiated geometry.
4. Using `texelFetch()` in GLSL to retrieve buffer data securely by index.

---

## The Concept of Instancing
Historically, rendering 10,000 spheres meant doing this:
```python
for position in array_of_spheres:
    setup_position(position)
    glDrawElements(...)
```
This forces the CPU to constantly freeze and swap context with the GPU 10,000 times, causing huge driver overhead bottlenecks. 

**Instanced Geometry** fixes this:
```python
glDrawElementsInstanced(..., 10000)
```
The CPU sends one command. The GPU figures out how to duplicate the objects and executes the shader 10,000 times natively. But if it duplicates it exactly, all objects will overlap perfectly.

### `gl_InstanceIDARB`
This built-in GLSL variable counts from `0` to `n_instances - 1`. 
The vertex shader can read `gl_InstanceIDARB` and apply a unique visual transformation based entirely on its array index.

---

## Using Texture Buffer Objects (`ARB_texture_buffer_object`)

To give each index a unique property (like a `vec3` offset), we can upload a giant array of points to the VBO as a "Texture". Notice we aren't sampling a 2D image. It is essentially random access memory structured as a texture.

```python
self.offset_array = (
    # generate random RGBA array...
    random.random( size=(count,4 ) ) * scale + offset
).astype('f')

TEXTURE_BUFFER_UNIFORM = TextureBufferUniform(
    name='offsets_table',
    format='RGBA32F',
    value = ShaderBuffer(
        usage = 'STATIC_DRAW',
        type = 'TEXTURE',
        buffer = self.offset_array,
    ),
)
```

> **Why `RGBA32F` (4 components)?**
> `TextureBufferObjects` have strict compatibility. 1-, 2-, and 4-component configurations are universally accepted as safe padding. Even though we only need 3 floats (`xyz`), we pad with a fourth (`w`) to maintain `< OpenGL 4.x` backward compatibility natively.

---

## Retrieving the Data in the Vertex Shader 

Our Vertex Shader defines a special sampler: `samplerBuffer`. 
We pull our pre-generated offset positions by matching `gl_InstanceIDARB` inside `offsets_table` via `texelFetch()`:

```glsl
uniform samplerBuffer offsets_table;

void main() {
    // 1. Get the translation offset for THIS specific instance
    vec3 offset = texelFetch( offsets_table, gl_InstanceIDARB ).xyz;
    
    // 2. Add the unique offset to the base sphere geometry
    vec3 final_position = Vertex_position + offset;
    
    // 3. Complete normal vertex shader tasks
    gl_Position = gl_ModelViewProjectionMatrix * vec4(final_position, 1.0);
    // ...
}
```

By pushing this logic, our Python program just binds the matrices and buffers, and steps away. The GPU takes full control.

---

## Render Call

```python
glDrawElementsInstanced(
    GL_TRIANGLES, 
    self.count,
    GL_UNSIGNED_INT, 
    vbo,
    len(self.offset_array), # Let GPU know we want N instances
)
```

With one function call, thousands of uniquely placed, fully illuminated specular objects render seamlessly.

---

## Changing Code Infrastructure to PyOpenGL's High-Level Abstractions

This tutorial leverages OpenGLContext's `GLSLObject`, `FloatUniform1f`, `TextureUniform`, and `ShaderAttribute` high-level objects. This abstracts away tracking handles to locations via `glGetUniformLocation` manually, acting closer to a modern framework standard.

---

## Key Takeaways
| Concept | What to Remember |
|---------|-----------------|
| **`glDrawElementsInstanced`** | One call to render `N` objects simultaneously over GPU |
| **`gl_InstanceIDARB`** | Unique counting identifier per instance in vertex shader |
| **`TextureBufferObject`** | A 1D array of floats passed to the GPU mapped as a flat texture |
| **`texelFetch(buffer, id)`** | Safe index lookup in GLSL to fetch exact properties |
| **RGBA Format Requirement** | Legacy requirement to pad 3-float vectors into 4-float vectors for 1D float textures. |

---

## Conclusion
This concludes the core of lighting, shadows, and optimization scaling in GLSL via PyOpenGL. The capabilities to render instances at scale will open pathways to generate massive particle/asteroid physics fields.
