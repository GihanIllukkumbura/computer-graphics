# Tutorial 04: Triangle Rotation (2D Transformations) — Teaching Guide

## Overview
This tutorial demonstrates **2D geometric transformations** — specifically **rotation about an arbitrary point**. While the previous tutorials focused on *rasterising* shapes (deciding which pixels to plot), this tutorial focuses on *transforming* shapes (moving, rotating, scaling them before drawing).

**Based on**: `TriangleRotation.java`

---

## Prerequisites and Setup

```powershell
cd tutorials\lineDrawing
python 04_triangle_rotation.py
```

**Expected Output:** A blue triangle (original) and a red triangle (rotated 45° about the first vertex). The rotation matrix is displayed on screen.

**Controls:**
- **←/→ Arrow Keys** — Decrease/increase rotation angle by 5°
- **Click** — Move the pivot (rotation centre) point
- **R** — Reset to defaults
- **ESC** — Exit

---

## Learning Objectives

By the end of this tutorial, students will understand:
1. The **2D rotation matrix** and how to derive it
2. **Rotation about an arbitrary point** (translate-rotate-translate)
3. The difference between rotating about the origin vs an arbitrary pivot
4. How Java's `AffineTransform` maps to manual matrix math
5. Radians vs degrees conversion

---

## What is a 2D Transformation?

A transformation changes a point's position. The three fundamental 2D transformations are:

```
Translation:    (x', y') = (x + tx, y + ty)
Scaling:        (x', y') = (sx * x, sy * y)
Rotation:       (x', y') = (x*cosθ - y*sinθ,  x*sinθ + y*cosθ)
```

All three can be combined into a single **transformation matrix** using homogeneous coordinates.

---

## The 2D Rotation Matrix

### Rotation About the Origin

To rotate a point (x, y) by angle θ around the **origin (0, 0)**:

```
┌ x' ┐   ┌ cos(θ)  -sin(θ) ┐   ┌ x ┐
│    │ = │                  │ × │   │
└ y' ┘   └ sin(θ)   cos(θ) ┘   └ y ┘
```

**Expanded:**
```
x' = x·cos(θ) - y·sin(θ)
y' = x·sin(θ) + y·cos(θ)
```

### Derivation (Why Does This Work?)

Consider a point P at angle α and distance r from origin:
```
x = r·cos(α)
y = r·sin(α)
```

After rotating by θ:
```
x' = r·cos(α + θ) = r·cos(α)·cos(θ) - r·sin(α)·sin(θ) = x·cos(θ) - y·sin(θ)  ✓
y' = r·sin(α + θ) = r·cos(α)·sin(θ) + r·sin(α)·cos(θ) = x·sin(θ) + y·cos(θ)  ✓
```

---

## Rotation About an Arbitrary Point

The Java code rotates about vertex (x1, y1):
```java
AffineTransform transform = new AffineTransform();
transform.rotate(Math.toRadians(rotationDegrees), x1, y1);
```

This is equivalent to THREE steps:

```
Step 1: TRANSLATE pivot to origin
   (x, y) → (x - px, y - py)

Step 2: ROTATE about origin
   Apply the rotation matrix

Step 3: TRANSLATE back
   (x', y') → (x' + px, y' + py)
```

### Python Implementation:

```python
def rotate_point(x, y, pivot_x, pivot_y, angle_degrees):
    angle_rad = math.radians(angle_degrees)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # Step 1: Translate to origin
    dx = x - pivot_x
    dy = y - pivot_y

    # Step 2: Rotate
    new_x = cos_a * dx - sin_a * dy
    new_y = sin_a * dx + cos_a * dy

    # Step 3: Translate back
    return new_x + pivot_x, new_y + pivot_y
```

### Visual:

```
Before rotation (45°):        After rotation:

    P3(250,150)                     P3'
     ╱╲                           ╱╲
    ╱  ╲                         ╱  ╲
   ╱    ╲                       ╱    ╲
  ╱______╲                     ╱______╲
P1(200,200) P2(300,300)    P1=pivot    P2'

Pivot point P1 doesn't move (it rotates around itself = stays put).
```

---

## Java vs Python Comparison

| Aspect | Java (TriangleRotation.java) | Python (04_triangle_rotation.py) |
|--------|------------------------------|----------------------------------|
| Rotation | `AffineTransform.rotate()` | Manual matrix multiplication |
| Drawing | `g2d.drawLine(x1,y1,x2,y2)` | `pygame.draw.line(surface, ...)` |
| Angle input | Hard-coded `45°` | Interactive arrow keys |
| Pivot | Fixed at P1 | Click anywhere to move |
| Matrix visible | Hidden inside AffineTransform | Displayed on screen |

**Key teaching point:** Java's `AffineTransform` hides the mathematics. Our Python version makes the matrix explicit so students understand what's happening.

---

## Important Angle Concepts

### Degrees vs Radians
```
360° = 2π radians
 90° = π/2 radians
 45° = π/4 radians

Conversion:
  radians = degrees × (π / 180)
  degrees = radians × (180 / π)
```

Python: `math.radians(45)` → `0.7854...`

### Rotation Direction
```
Positive angle = Counter-clockwise (in standard math)
                = Clockwise in screen coords (Y is flipped!)

This is why the Java code appears to rotate differently
than you might expect — screen Y is inverted.
```

---

## Worked Example

**Rotate point (300, 300) by 45° about pivot (200, 200):**

```
Step 1: Translate to origin
  dx = 300 - 200 = 100
  dy = 300 - 200 = 100

Step 2: Rotate by 45°
  cos(45°) = 0.7071
  sin(45°) = 0.7071

  new_x = 0.7071 × 100 - 0.7071 × 100 = 0
  new_y = 0.7071 × 100 + 0.7071 × 100 = 141.42

Step 3: Translate back
  final_x = 0 + 200 = 200
  final_y = 141.42 + 200 = 341.42

Result: (300, 300) → (200, 341)
```

The point moves from the bottom-right to directly below the pivot (in screen coordinates).

---

## Homogeneous Coordinates (Advanced)

For efficiency, we can combine translate-rotate-translate into a **single 3×3 matrix**:

```
┌ x' ┐   ┌ cos(θ)  -sin(θ)  tx ┐   ┌ x ┐
│ y' │ = │ sin(θ)   cos(θ)  ty │ × │ y │
└  1 ┘   └   0        0      1 ┘   └ 1 ┘

Where:
  tx = px - px·cos(θ) + py·sin(θ)
  ty = py - px·sin(θ) - py·cos(θ)
```

This is exactly what Java's `AffineTransform` stores internally. One matrix multiplication replaces three separate operations.

---

## Exercises

### Exercise 1: Verify the Rotation
Calculate by hand the rotation of point (250, 150) by 45° about pivot (200, 200). Then run the program to verify your answer matches the red triangle's P3' position.

```
Given: P3 = (250, 150), pivot = (200, 200), θ = 45°

dx = 250 - 200 = 50
dy = 150 - 200 = -50

x' = cos(45°)×50 - sin(45°)×(-50) = 35.36 + 35.36 = 70.71
y' = sin(45°)×50 + cos(45°)×(-50) = 35.36 - 35.36 = 0

Result: (70.71 + 200, 0 + 200) = (270.71, 200)
```

### Exercise 2: Rotation About the Centroid
Modify the program to rotate about the **centroid** (centre of mass) of the triangle instead:

```python
def centroid(p1, p2, p3):
    cx = (p1[0] + p2[0] + p3[0]) / 3
    cy = (p1[1] + p2[1] + p3[1]) / 3
    return (cx, cy)

pivot = centroid(tri_p1, tri_p2, tri_p3)
```

### Exercise 3: Continuous Animation
Make the triangle rotate continuously by incrementing the angle each frame:

```python
# In the main loop, replace keyboard controls with:
rotation_angle += 1  # 1 degree per frame
if rotation_angle >= 360:
    rotation_angle -= 360
```

### Exercise 4: Multiple Rotations
Draw the triangle at 30° intervals (0°, 30°, 60°, ... 330°) to create a flower-like pattern:

```python
for angle in range(0, 360, 30):
    r1 = rotate_point(tri_p1[0], tri_p1[1], pivot[0], pivot[1], angle)
    r2 = rotate_point(tri_p2[0], tri_p2[1], pivot[0], pivot[1], angle)
    r3 = rotate_point(tri_p3[0], tri_p3[1], pivot[0], pivot[1], angle)
    draw_triangle(screen, r1, r2, r3, some_color)
```

### Exercise 5: Scaling Transformation
Add a scaling transformation to the program. Scale factor should be adjustable with UP/DOWN keys:

```python
def scale_point(x, y, pivot_x, pivot_y, sx, sy):
    """Scale point (x,y) relative to pivot by factors (sx, sy)."""
    dx = x - pivot_x
    dy = y - pivot_y
    return dx * sx + pivot_x, dy * sy + pivot_y
```

### Exercise 6: Combined Transform (Scale + Rotate)
Combine scaling and rotation into a single operation. Apply scale first, then rotation:

```python
def transform_point(x, y, px, py, angle, sx, sy):
    # Scale first
    x2, y2 = scale_point(x, y, px, py, sx, sy)
    # Then rotate
    return rotate_point(x2, y2, px, py, angle)
```

Try scale=0.5 with angle=45° — the triangle should be half-sized and rotated.

---

## Common Student Questions

**Q: Why does the triangle appear to rotate clockwise when using positive angles?**
A: In screen coordinates, the Y-axis is inverted (positive = downward). This flips the rotation direction. In standard math coordinates, positive angles rotate counter-clockwise.

**Q: What happens if I rotate by 360°?**
A: The point returns to its original position: `cos(360°) = 1`, `sin(360°) = 0`, so the rotation matrix becomes the identity matrix.

**Q: Can I rotate about a point that's not a vertex?**
A: Yes! Click anywhere in the program to move the pivot point. The algorithm works for any pivot.

**Q: Why is `math.radians()` needed?**
A: Python's `math.cos()` and `math.sin()` take radians, not degrees. Forgetting this conversion is a very common bug: `cos(45)` ≠ `cos(π/4)`.

**Q: How does this relate to 3D rotation?**
A: 3D rotation extends this concept to three planes (XY, XZ, YZ). Each uses the same 2D rotation matrix applied to two of the three axes. This leads to Euler angles, quaternions, and rotation matrices used in 3D graphics.

---

## Debugging Tips

**Problem: Triangle disappears after rotation**
- Large rotation angles with extreme pivots can move the triangle off-screen
- Press R to reset, or click to move the pivot closer to the triangle

**Problem: Rotation looks "wrong" compared to expectations**
- Remember screen Y is inverted
- Positive angles rotate clockwise on screen (counter-clockwise in math)

**Problem: Floating-point artefacts after many rotations**
- Always rotate from the original points, not from the previously rotated ones
- The program does this correctly: it recalculates from `tri_p1, tri_p2, tri_p3` each frame

---

## Key Takeaways

| Concept | What to Remember |
|---------|-----------------|
| **Rotation matrix** | `[cos θ, -sin θ; sin θ, cos θ]` |
| **Arbitrary pivot** | Translate → Rotate → Translate back |
| **Degrees → Radians** | `radians = degrees × π/180` |
| **Screen vs Math** | Y-axis is flipped; rotation direction reverses |
| **Identity at 360°** | Full rotation returns to start |
| **AffineTransform** | Java hides the matrix; we make it explicit |

---

## Summary: The 4-Tutorial Series

```
Tutorial 01: Point Drawer     — The primitive: plotting a single pixel
Tutorial 02: Bresenham Line    — Connecting two points efficiently (integer math)
Tutorial 03: Bresenham Circle  — Drawing curves with 8-way symmetry
Tutorial 04: Triangle Rotation — Transforming shapes with matrices
```

**These form the foundation of 2D computer graphics:**
- Rasterisation (which pixels to light up)
- Transformations (how to move/rotate/scale shapes)
- Together, they are used in everything from GUIs to video games to CAD software
