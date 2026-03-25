# Tutorial 10: Spot Lights — Teaching Guide

## Overview
This tutorial builds on the concept of Point Lights to create **Spot Lights** — directional shielded point lights. Instead of emitting light in a full 360-degree sphere, spot lights emit light only within a specific cone, and have an exponent function that determines how concentrated the light is in the center of the beam.

**Based on:** OpenGLContext `shader_9.py`

---

## Prerequisites and Setup
Builds on Tutorial 09 (Point Lights). Students should understand:
- Point light coordinate setup and distance attenuation.
- The distinction between a light's location (where it is) and a generic directional vector (where it points).

---

## Learning Objectives
By the end of this tutorial, students will understand:
1. How a spot light differs from a point light conceptually.
2. The role of the `spot_direction` vector.
3. How `cos_spot_cutoff` restricts lighting to a given cone angle.
4. How the `spot_exponent` controls the "focus" or "softness" of the spot edge.

---

## Expanding the Light Properties

To support spotlights, we add 2 more `vec4` properties per light, increasing `LIGHT_SIZE` to 7:

```glsl
// SPOT_PARAMS [cos_spot_cutoff, spot_exponent, ignored, is_spot]
const int SPOT_PARAMS = 5;
// SPOT_DIR    [x, y, z, ignored] model-space direction
const int SPOT_DIR = 6;
```

### The Spot Parameters (`SPOT_PARAMS`)
- **`x (cos_spot_cutoff)`**: The cosine of the angle defining the spotlight's cone. We use cosine to allow fast `dot()` product comparisons without calling `acos()`.
- **`y (spot_exponent)`**: Defines the softness of the beam. A higher exponent focuses more light towards the center axis. A lower exponent produces a flatter light distribution, resembling a hard cut-off shield.
- **`w (is_spot)`**: A toggle flag. `0.0` means the light is a normal point/directional light. `1.0` enables spotlight calculations.

### The Spot Direction (`SPOT_DIR`)
This defines the central axis of the spotlight. It determines the direction the spotlight is "pointing" from its `POSITION`.

---

## The Spotlight GLSL Calculation

Inside `phong_weightCalc` in our fragment shader, we add the spotlight filter logic:

```glsl
float spot_effect = 1.0;

if (spot_params.w != 0.0) { // is a spot...
    // Calculate cosine of the angle between light-to-fragment and spot direction
    float spot_cos = dot(
        gl_NormalMatrix * normalize(spot_direction.xyz),
        normalize(-light_pos)
    );
    
    // Check if fragment is outside the cone
    if (spot_cos <= spot_params.x) {
        return vec3(0.0, 0.0, 0.0); // No light outside the spot cone!
    } else {
        if (spot_cos == 1.0) {
            spot_effect = 1.0;
        } else {
            // Calculate falloff/focus based on the exponent
            spot_effect = pow(
                (1.0 - spot_params.x) / (1.0 - spot_cos),
                spot_params.y
            );
        }
    }
}
```

### Mathematical Breakdown
1. **`normalize(-light_pos)`**: Vector from the light's position pointing *towards* the fragment.
2. **`dot()` product**: We take the dot product of the spot's central direction and our fragment vector. Because both are normalized, this gives us the **cosine of the angle** between them.
3. **Cut-off Check**: If `spot_cos` is smaller than or equal to `cos_spot_cutoff` (meaning the angle is *larger* than our limit), the fragment is entirely in the dark. `return vec3(0.0, 0.0, 0.0)`.
4. **Exponent Calculation**: We calculate a fractional representation of where the fragment falls from the center (1.0) to the edge cutoff (0.0). We raise this fraction to the `spot_exponent`.

Finally, we apply `spot_effect` to the specular `n_dot_half` calculation (which controls the highlight reflection) so that specular highlights fade nicely at the spot edge:

```glsl
n_dot_half *= spot_effect;
```

*(Note: The tutorial's spot calculation uses a custom mathematical approach prioritizing computational stability over perfect legacy OpenGL emulation).*

---

## Python Configuration

Let's look at one of the configured spotlights from the Python code:

```python
# Light 0 properties
('lights[0].position', (2.5, 3.5, 2.5, 1.0)),     # w=1.0 is Point Light
('lights[0].spot_params', (cos(.25), 1.0, 0.0, 1.0)), # Cutoff angle ~14 degrees (.25 rad), Exp=1.0, is_spot=1.0
('lights[0].spot_dir', (-8, -20, -8.0, 1.0))      # Points downwards and leftwards
```

The combination of position, direction, and cut-off creates a defined cone of illumination.

---

## Key Takeaways
- Spot lights apply an angle-based "mask" over a point light.
- **Dot products** are your best friend in shader math. We compare angles entirely in cosine space to save computational time.
- Passing structured groupings of properties via flat arrays (like `lights`) scales smoothly.

---

## What's Next
This completes our robust multi-light Blinn-Phong renderer. In the next tutorial, we shift focus from fragment calculation optimizations to **vertex throughput optimizations**, introducing **Instanced Geometry** and **Texture Buffer Objects**.
