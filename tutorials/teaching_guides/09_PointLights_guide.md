# Tutorial 09: Point Lights — Teaching Guide

## Overview
This tutorial introduces **Point Lights** and the concept of **Light Attenuation** (light fall-off). We'll modify our renderer to handle both directional lights (no position, infinitely far) and point lights (has a position, falls off over distance) dynamically using the `.w` component of the light's position vector, just as legacy OpenGL does.

**Based on:** OpenGLContext `shader_8.py`

---

## Prerequisites and Setup
Builds on Tutorial 08 (Optimizations). Students should understand:
- How to separate calculations into the vertex and fragment shaders.
- That interpolating `varying` variables acts as a per-pixel approximation.

---

## Learning Objectives
By the end of this tutorial, students will understand:
1. How point lights differ from directional lights.
2. How to compute the distance and direction to a point light at each vertex.
3. How to use **Linear, Constant, and Quadratic Attenuation** to control how the light falls off.
4. How the `w` component dynamically controls whether a light calculation uses distance or not.

---

## Directional vs. Point Lights

A directional light treats every point in space as having the exact same light direction vector, meaning it's infinitely far away. A **point light** exists at a specific location, so the light direction vector to a fragment will differ depending on the fragment's position. Also, point lights spread outwards and grow dimmer over distance (attenuation).

### Distance and Attenuation
We use a 3-element vector to control attenuation:
`attenuations = (constant, linear, quadratic)`

```glsl
attenuation = clamp(0.0, 1.0, 1.0 / (
    attenuations.x +
    (attenuations.y * distance) +
    (attenuations.z * distance * distance)
));
```
- Smaller values here mean the light stays brighter for longer.
- `(1.0, 0.0, 0.0)` implies no attenuation (default OpenGL).

---

## The Vertex Stage Pre-Calculations

We define two helper functions in our vertex shader block to handle the complex math cleanly.

### `phong_preCalc`
 This determines distance and direction, switching behavior using `w`:
 
```glsl
if (light_position.w == 0.0) {
    // Directional Light
    ec_light_location = normalize( gl_NormalMatrix * light_position.xyz );
    light_distance = 0.0; // no attenuation
} else {
    // Point Light
    vec3 ms_vec = (light_position.xyz - vertex_position);
    ec_light_location = normalize( gl_NormalMatrix * ms_vec );
    light_distance = abs(length( ms_vec ));
}
```

### `light_preCalc`
 This simply loops through all `LIGHT_COUNT` lights, calling `phong_preCalc` on each and storing the results into our `varying vec3` arrays.

---

## Using Attenuation in `phong_weightCalc`

In the fragment shader, we have modified the `phong_weightCalc` to output a `vec3(ambientMult, diffuseMult, specularMult)`. 

If the light has distance, we multiply the diffuse and specular multipliers by our calculated attenuation clamp:
```glsl
if (distance != 0.0) {
    // calculate attenuation...
    n_dot_pos *= attenuation;   // diffuse
    n_dot_half *= attenuation;  // specular
}
```

Notably, by returning `ambientMult` (which is simply the `attenuation` output), our new lights can restrict ambient lighting per-light so that ambient glow is also restricted by attenuation.

---

## Light Configurations
Our Python code has three colored lights using `w=1.0` (point light toggle):

| Color | Attenuation | Effect |
| --- | --- | --- |
| Green | `0.0, 0.15, 0.0` (linear) | Gradual falloff |
| Red | `0.0, 0.0, 0.15` (quadratic) | Sharper falloff at the beginning |
| Blue | `0.15, 0.0, 0.0` (constant) | Farthest throw, no actual falloff distance curve |

*A `W` coordinate of 0.0 acts as a directional light! It skips attenuation and treats the given coordinates as a general light direction instead.*

---

## Key Takeaways
- Always inspect the `w` coordinate! `w=1` is a point in space (Point Light). `w=0` is a distant direction (Directional).
- Attenuation is highly configurable (`constant`, `linear`, `quadratic`) depending on the physical aesthetic desired.
- Calculating dynamic distance per vertex and sharing across varying variables is key to keeping performance tight.

---

## What's Next
Next, we expand Point Lights into **Spot Lights**, allowing us to block light out of a given cone path, rather than lighting in a full 360-degree sphere.
