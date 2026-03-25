# Tutorial 02: Bresenham's Line Algorithm — Teaching Guide

## Overview
This tutorial implements **Bresenham's Line Algorithm**, the most important rasterisation algorithm in computer graphics. It draws straight lines between two points using **only integer arithmetic** — no floating-point multiplication or division. This makes it extremely fast and suitable for hardware implementation.

**Based on**: `Bresenhams.java`

---

## Prerequisites and Setup

```powershell
cd tutorials\lineDrawing
python 02_bresenham_line.py
```

**Expected Output:** A window with a pre-drawn green line from (100,100) to (800,200). Click two points to draw additional lines.

**Controls:**
- **Click** two points — Draw a line between them
- **D** — Toggle debug/step mode
- **SPACE** — Next step (in debug mode)
- **R** — Reset
- **ESC** — Exit

---

## Learning Objectives

By the end of this tutorial, students will understand:
1. Why naive line drawing (`y = mx + c`) is inefficient
2. The **decision parameter** `p` and how it avoids floating-point math
3. How the algorithm decides between two candidate pixels at each step
4. How to extend the algorithm to handle **all 8 octants**
5. How to trace the algorithm step-by-step with a table

---

## Why Not Just Use y = mx + c?

The naive approach:
```python
def naive_line(x1, y1, x2, y2):
    m = (y2 - y1) / (x2 - x1)   # slope (FLOAT division!)
    c = y1 - m * x1              # y-intercept
    for x in range(x1, x2 + 1):
        y = m * x + c            # FLOAT multiplication every pixel!
        plot(x, round(y))
```

**Problems:**
1. **Floating-point division** to compute slope — expensive on old hardware
2. **Floating-point multiplication** for every single pixel
3. **Rounding errors** accumulate over long lines
4. Doesn't handle **vertical lines** (division by zero)
5. **Gaps** appear for steep lines (|slope| > 1)

---

## The Bresenham Key Insight

Instead of computing the exact y-coordinate, we keep track of the **error** (how far we've drifted from the true line) and make a binary decision at each step:

```
Should the next pixel go → STRAIGHT or → DIAGONAL?

                    ●  ← diagonal (x+1, y+1)
         True line /
        ─ ─ ─ ─ /─ ─ ─
               /
Current ● ── ● ── ●  ← straight (x+1, y)
```

The **decision parameter** `p` tells us which pixel is closer to the true line.

---

## The Algorithm — Step by Step

### For gentle slopes (|slope| ≤ 1, octant 1):

```
Given: line from (x1, y1) to (x2, y2)

1. Calculate:
   dx = |x2 - x1|
   dy = |y2 - y1|

2. Initial decision parameter:
   p = 2*dy - dx

3. For each step (increment x by 1):
   if p < 0:
       → plot (x, y)        // stay at same y
       → p = p + 2*dy       // update p
   else:
       → plot (x, y)
       → y = y + 1          // move y up too
       → p = p + 2*(dy-dx)  // update p
```

### The Decision Parameter Derivation

Starting from the line equation `F(x,y) = dy·x - dx·y + c = 0`:

```
At each step, we choose between:
  Upper pixel: (x+1, y+1)
  Lower pixel: (x+1, y)

Distance to upper:  d1 = y - y_true
Distance to lower:  d2 = y_true - y

Decision = d1 - d2
         = 2*dy*x - 2*dx*y + c   (scaled by 2 to avoid fractions)

This is our decision parameter p.
```

**The beauty**: updating `p` only requires **addition and subtraction** — no multiplication per pixel (the `2*dy` and `2*(dy-dx)` are computed once before the loop).

---

## Java to Python Translation

### Original Java (Octant 1 only):
```java
dx = Math.abs(x2 - x1);
dy = Math.abs(y2 - y1);
x = x1;  y = y1;
p = 2 * dy - dx;

g.fillOval(x1, y1, 1, 1);   // plot first point

for (k = 0; k < dx; k++) {
    if (p < 0) {
        g.fillOval(x++, y, 1, 1);     // plot, move x
        p = (p + (2 * dy));
    } else {
        g.fillOval(x++, y++, 1, 1);   // plot, move x AND y
        p = (p + (2 * (dy - dx)));
    }
}
```

### Python (All 8 octants):
```python
def bresenham_line(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1    # step direction for x
    sy = 1 if y1 < y2 else -1    # step direction for y

    x, y = x1, y1
    points = [(x, y)]

    if dx >= dy:
        # Gentle slope: step in x (same as Java)
        p = 2 * dy - dx
        for k in range(dx):
            if p < 0:
                x += sx
                p = p + (2 * dy)
            else:
                x += sx
                y += sy
                p = p + (2 * (dy - dx))
            points.append((x, y))
    else:
        # Steep slope: swap roles of x and y
        p = 2 * dx - dy
        for k in range(dy):
            if p < 0:
                y += sy
                p = p + (2 * dx)
            else:
                y += sy
                x += sx
                p = p + (2 * (dx - dy))
            points.append((x, y))

    return points
```

**Key differences from Java:**
- `sx, sy` handle any direction (Java only handled left-to-right, top-to-bottom)
- The `else` branch handles steep slopes by swapping x and y roles
- Returns a list of points instead of drawing immediately

---

## The 8 Octants

A line can go in any of 8 directions. The original Java code only handles **Octant 1**:

```
              Octant 2 (steep +)
         \    |    /
  Oct 3   \   |   /   Octant 1 (gentle +) ← Java handles this one
   (steep) \  |  /
             \|/
  ─────────── ● ──────────  Octant 0 (horizontal)
             /|\
   Oct 4    / | \   Octant 8 (gentle -)
  (steep)  /  |  \
          /   |   \
              Octant 5 (steep -)
```

Our Python handles all 8 by:
1. Using `sx` and `sy` for direction
2. Swapping x/y roles for steep lines (`dx < dy`)

---

## Worked Example: Trace Table

**Line from (2, 3) to (12, 8):**

```
dx = |12-2| = 10
dy = |8-3|  = 5
p_initial = 2*5 - 10 = 0

2*dy     = 10
2*(dy-dx) = -10
```

| Step k | x  | y | p (before) | Decision | p (after) |
|--------|----|---|------------|----------|-----------|
| start  | 2  | 3 | 0          |          |           |
| 0      | 3  | 4 | 0 ≥ 0     | diagonal | 0+(-10)=-10 |
| 1      | 4  | 4 | -10 < 0   | straight | -10+10=0  |
| 2      | 5  | 5 | 0 ≥ 0     | diagonal | 0+(-10)=-10 |
| 3      | 6  | 5 | -10 < 0   | straight | -10+10=0  |
| 4      | 7  | 6 | 0 ≥ 0     | diagonal | 0+(-10)=-10 |
| 5      | 8  | 6 | -10 < 0   | straight | -10+10=0  |
| 6      | 9  | 7 | 0 ≥ 0     | diagonal | 0+(-10)=-10 |
| 7      | 10 | 7 | -10 < 0   | straight | -10+10=0  |
| 8      | 11 | 8 | 0 ≥ 0     | diagonal | 0+(-10)=-10 |
| 9      | 12 | 8 | -10 < 0   | straight | -10+10=0  |

**Pattern:** diagonal-straight-diagonal-straight... (slope = 0.5 = alternating)

---

## Visual: How the Decision Parameter Works

```
True line (slope = 0.5):

y  5 ┤              ●
     │           ● /
   4 ┤        ● / ●
     │     ● / ●
   3 ┤  ● / ●
     │● / ●
   2 ┤─────────────────
     2  3  4  5  6  7  x

When p < 0: the true line is closer to the lower pixel → go straight
When p ≥ 0: the true line is closer to the upper pixel → go diagonal

The algorithm alternates to stay as close as possible to the true line.
```

---

## Exercises

### Exercise 1: Trace a Line by Hand
Trace Bresenham's algorithm for the line from **(1, 1) to (8, 5)**:
- Calculate dx, dy, initial p
- Fill in a trace table like the example above
- Verify by running in debug mode (press D, then click the two points)

### Exercise 2: Steep Line
Draw a line from **(100, 100) to (150, 400)** — this is a steep line (|slope| > 1).
Observe that the algorithm steps in y instead of x. How many pixels are plotted?

**Answer code:**
```python
pixels = bresenham_line(100, 100, 150, 400)
print(f"Pixels plotted: {len(pixels)}")
# Should be 301 (same as dy + 1 = 300 + 1)
```

### Exercise 3: All 8 Directions
Draw 8 lines radiating from the center (400, 350) in all octant directions. Verify each works:

```python
import math
center = (400, 350)
length = 200
for angle in range(0, 360, 45):
    rad = math.radians(angle)
    end_x = int(center[0] + length * math.cos(rad))
    end_y = int(center[1] + length * math.sin(rad))
    pixels = bresenham_line(center[0], center[1], end_x, end_y)
    # Draw pixels...
```

### Exercise 4: Draw a Triangle
Use three Bresenham lines to draw a triangle:
```python
def draw_triangle(x1, y1, x2, y2, x3, y3):
    line1 = bresenham_line(x1, y1, x2, y2)
    line2 = bresenham_line(x2, y2, x3, y3)
    line3 = bresenham_line(x3, y3, x1, y1)
    return line1 + line2 + line3
```

### Exercise 5: Speed Comparison
Time the DDA (floating-point) approach vs Bresenham for 10,000 lines:

```python
import time

def dda_line(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return [(x1, y1)]
    x_inc = dx / steps
    y_inc = dy / steps
    points = []
    x, y = float(x1), float(y1)
    for _ in range(steps + 1):
        points.append((round(x), round(y)))
        x += x_inc
        y += y_inc
    return points

# Time both
start = time.time()
for _ in range(10000):
    dda_line(0, 0, 500, 300)
dda_time = time.time() - start

start = time.time()
for _ in range(10000):
    bresenham_line(0, 0, 500, 300)
bres_time = time.time() - start

print(f"DDA: {dda_time:.3f}s  Bresenham: {bres_time:.3f}s")
```

### Exercise 6: Dashed Lines
Modify `bresenham_line` to draw dashed lines by only plotting every other N pixels:

```python
def bresenham_dashed(x1, y1, x2, y2, dash_length=5):
    all_points = bresenham_line(x1, y1, x2, y2)
    dashed = []
    for i, pt in enumerate(all_points):
        if (i // dash_length) % 2 == 0:
            dashed.append(pt)
    return dashed
```

---

## Common Student Questions

**Q: Why is integer-only important? Modern CPUs have fast floating-point!**
A: True for CPUs, but this algorithm was designed when it mattered enormously. It's still relevant because: (1) GPUs implement it in hardware, (2) embedded systems may lack FPU, (3) integer math is deterministic — no rounding surprises.

**Q: What happens when dx = 0 (vertical line)?**
A: The steep-slope branch handles it — we step in y only, and dx=0 means p starts negative and never goes positive, so x never changes.

**Q: Why does the Java code only handle one octant?**
A: It's a simplified teaching example. Real implementations must handle all cases. Our Python version adds the `sx`, `sy` direction variables and the steep/gentle branching.

**Q: The decision parameter `p` can get very large for long lines. Is overflow a concern?**
A: In theory yes, but `p` oscillates around 0 (it gets pulled back by the `2*(dy-dx)` correction). For 32-bit integers, lines up to ~1 billion pixels long are safe.

---

## Debugging Tips

**Problem: Line only draws in one direction**
- Check `sx` and `sy` — they must be -1 or +1 depending on the direction

**Problem: Gaps in steep lines**
- You must swap x/y roles when `dy > dx` — check the `else` branch

**Problem: Off-by-one (line stops one pixel short)**
- The loop runs `dx` (or `dy`) times, and we plot the start point before the loop = dx+1 total pixels

**Visualise the true line alongside:**
```python
# Draw the "mathematical" line in grey first
pygame.draw.line(screen, (200,200,200), (x1,y1), (x2,y2), 1)
# Then draw Bresenham pixels on top
```

---

## Key Takeaways

| Concept | What to Remember |
|---------|-----------------|
| **Decision parameter** | `p = 2*dy - dx` initially; updated with additions only |
| **p < 0** | Next pixel goes straight (don't change minor axis) |
| **p ≥ 0** | Next pixel goes diagonal (change both axes) |
| **Gentle slope** | Step in x, decide on y |
| **Steep slope** | Step in y, decide on x |
| **Integer only** | No division, no multiplication per pixel |

---

## What's Next

Now that we can draw lines, the next tutorial applies a similar integer-arithmetic approach to drawing **circles** — Bresenham's Circle Algorithm uses 8-way symmetry to compute only 1/8 of the circle.
