# Bresenham Circle Drawing Theory (Easy Step-by-Step)

This note explains the theory behind circle drawing in:
- 03_bresenham_circle.py

The algorithm is also called the Midpoint Circle Algorithm.

---

## 1) What Problem Are We Solving?

We need to draw a circle of radius r centered at (xc, yc) on a pixel grid.
A perfect circle is continuous, but the screen is discrete.
So, at each step, we choose the best pixel to approximate the true circle.

---

## 2) Circle Equation and Decision Logic

For a circle centered at origin:

x^2 + y^2 = r^2

Define:

F(x, y) = x^2 + y^2 - r^2

1. F < 0 means point is inside the circle.
2. F = 0 means point is on the circle.
3. F > 0 means point is outside the circle.

At each step we test a midpoint to decide whether y should stay same or decrease.

---

## 3) Biggest Idea: 8-Way Symmetry

If one point (x, y) is on the circle, then these 8 points are also on the circle around center (xc, yc):

1. (xc + x, yc + y)
2. (xc + x, yc - y)
3. (xc - x, yc + y)
4. (xc - x, yc - y)
5. (xc + y, yc + x)
6. (xc + y, yc - x)
7. (xc - y, yc + x)
8. (xc - y, yc - x)

So we compute one octant and mirror to all 8 parts.
This is the key speed-up.

---

## 4) Initial Values and Update Rules

Start from top point of circle in first octant:

- x = 0
- y = r
- p = 3 - 2*r

Loop while x <= y:

1. Plot 8 symmetric points.
2. If p < 0:
   - choose East pixel (x increases, y same)
   - p = p + 4*x + 6
3. Else:
   - choose South-East pixel (x increases, y decreases)
   - p = p + 4*(x - y) + 10
   - y = y - 1
4. x = x + 1

Stop when x > y (passed 45 degrees in first octant).

---

## 5) Step-by-Step Algorithm

### Step 1: Input

Given center (xc, yc) and radius r

### Step 2: Handle trivial case

If r == 0, circle is just one point: (xc, yc)

### Step 3: Initialize

- x = 0
- y = r
- p = 3 - 2*r

### Step 4: Repeat until x > y

1. Plot symmetric points for (x, y)
2. Apply decision using p
3. Update p
4. Increment x

### Step 5: Done

Collected points form the raster circle.

---

## 6) Worked Example (r = 5)

Initial:

- x = 0
- y = 5
- p = 3 - 10 = -7

| Step | x | y | p before | Decision | p after |
|---|---:|---:|---:|---|---:|
| 0 | 0 | 5 | -7 | start | -7 |
| 1 | 1 | 5 | -7 | p<0, y same | -1 |
| 2 | 2 | 5 | -1 | p<0, y same | 9 |
| 3 | 3 | 4 | 9  | p>=0, y--   | 7 |
| 4 | 4 | 3 | 7  | p>=0, y--   | 13 |

Stop after this because next x would exceed y.

At every row above, plot all 8 symmetric points around (xc, yc).

---

## 7) Why It Is Efficient

1. Integer math only.
2. One-octant computation with 8-way mirroring.
3. No trigonometric functions (no sin/cos required).
4. Very suitable for teaching and low-level rendering.

---

## 8) Tricky Scenarios

1. Small radius (r = 1 or 2):
   - many symmetric points overlap.
   - deduplicate points to avoid repeated plotting.
2. x == y case:
   - points on diagonal can duplicate; deduplicate helps.
3. Radius from mouse input can be 0:
   - handle as validation or single-point circle.
4. Coordinate-system confusion:
   - Cartesian vs screen coordinates must be converted correctly.

---

## 9) Mapping Theory to Your Python File

In 03_bresenham_circle.py:

1. circle_symmetric_points(...)
   - computes and deduplicates the 8 mirrored points.
2. bresenham_circle(...)
   - generates circle points from decision parameter logic.
3. bresenham_circle_trace(...)
   - returns each step with p and decision for debugging/teaching.

This makes your file excellent for both drawing and understanding the algorithm.

---

## 10) Quick Pseudocode

```text
function bresenham_circle(xc, yc, r):
    if r == 0: return [(xc, yc)]

    x = 0
    y = r
    p = 3 - 2*r
    points = symmetric_points(xc, yc, x, y)

    while x <= y:
        if p < 0:
            p = p + 4*x + 6
        else:
            p = p + 4*(x - y) + 10
            y = y - 1

        x = x + 1
        points += symmetric_points(xc, yc, x, y)

    return points
```

---

## 11) Practical Use Cases

1. Basic CAD and plotting tools
2. Game mini-maps and radar circles
3. UI rings, knobs, and circular indicators
4. Teaching rasterization fundamentals

---

## 12) Short Revision Summary

1. Circle algorithm starts at (0, r).
2. p decides if y stays or decreases.
3. Update with integer formulas only.
4. Plot one octant, mirror to 8 octants.
5. Stop when x crosses y.

This is the classic and efficient way to rasterize circles.
