# Tutorial 03: Bresenham's Circle Algorithm — Teaching Guide

## Overview
This tutorial implements the **Midpoint Circle Algorithm** (also called Bresenham's Circle), which draws circles using **integer arithmetic** and exploits **8-way symmetry** — you compute only 1/8 of the circle and mirror it to get the rest.

**Based on**: `BresenhamsCircle.java`

---

## Prerequisites and Setup

```powershell
cd tutorials\lineDrawing
python 03_bresenham_circle.py
```

**Expected Output:** A circle centred at (300, 300) with radius 200, with each octant drawn in a different colour.

**Controls:**
- **Click** — Set centre, then click again to set radius
- **O** — Toggle octant colouring
- **F** — Toggle filled circle mode
- **R** — Reset
- **ESC** — Exit

---

## Learning Objectives

By the end of this tutorial, students will understand:
1. Why **8-way symmetry** reduces computation by 8×
2. The **midpoint decision parameter** for circles
3. How the decision updates: `p + 4x + 6` vs `p + 4(x-y) + 10`
4. The connection between the circle equation and pixel selection
5. How to extend to filled circles using scan lines

---

## The Circle Equation

The implicit equation of a circle centred at origin with radius r:

```
F(x, y) = x² + y² - r² = 0

  If F(x,y) < 0  →  point is INSIDE the circle
  If F(x,y) = 0  →  point is ON the circle
  If F(x,y) > 0  →  point is OUTSIDE the circle
```

We use this to decide which pixel is closer to the true circle.

---

## 8-Way Symmetry

A circle is symmetric in 8 ways. Computing one octant (0° to 45°) gives you all 8 points:

```
Given a point (x, y) on the circle at centre (xc, yc):

        (-x,+y) ╲   (+x,+y)
                  ╲  |  ╱
       (-y,+x) ── ─ ● ─ ── (+y,+x)
                  ╱  |  ╲
        (-x,-y) ╱   (+x,-y)
               (-y,-x)  (+y,-x)
```

**The Java `plotCirclePoints` method:**
```java
g.drawLine(xc + x, yc + y, xc + x, yc + y);   // (x, y)
g.drawLine(xc + x, yc - y, xc + x, yc - y);   // (x, -y)
g.drawLine(xc - x, yc + y, xc - x, yc + y);   // (-x, y)
g.drawLine(xc - x, yc - y, xc - x, yc - y);   // (-x, -y)
g.drawLine(xc + y, yc + x, xc + y, yc + x);   // (y, x)   ← swapped!
g.drawLine(xc + y, yc - x, xc + y, yc - x);   // (y, -x)
g.drawLine(xc - y, yc + x, xc - y, yc + x);   // (-y, x)
g.drawLine(xc - y, yc - x, xc - y, yc - x);   // (-y, -x)
```

**Savings:** For radius 100, we compute ~14 pixels and get ~113 total (8× ≈ 112).

---

## The Algorithm

### Step-by-Step:

```
1. Start at the top of the circle: (x=0, y=r)
2. Initial decision parameter: p = 3 - 2*r
3. While x ≤ y (we're in the first octant):
   if p < 0:
       p = p + 4*x + 6     // next midpoint is inside → stay at same y
   else:
       p = p + 4*(x-y) + 10  // next midpoint is outside → decrease y
       y = y - 1
   x = x + 1
   plot 8 symmetric points
```

### Java to Python Comparison:

**Java:**
```java
int x = 0, y = r;
int p = 3 - (2 * r);

do {
    if (p < 0) {
        p = p + (4 * x) + 6;
    } else {
        p = p + (4 * (x - y)) + 10;
        y = y - 1;
    }
    x = x + 1;
    plotCirclePoints(g, xc, yc, x, y);
} while (x <= y);
```

**Python:**
```python
x, y = 0, r
p = 3 - (2 * r)

while x <= y:
    if p < 0:
        p = p + (4 * x) + 6
    else:
        p = p + (4 * (x - y)) + 10
        y -= 1
    x += 1
    plot_circle_points(xc, yc, x, y)
```

---

## Decision Parameter Derivation

The midpoint between the two candidate pixels is at `(x+1, y-0.5)`:

```
At each step, we choose:
  E pixel:  (x+1, y)    — move east (keep same y)
  SE pixel: (x+1, y-1)  — move south-east (decrease y)

Midpoint: M = (x+1, y-0.5)

Decision = F(M) = (x+1)² + (y-0.5)² - r²

If F(M) < 0: midpoint is INSIDE → circle passes above → choose E
If F(M) ≥ 0: midpoint is OUTSIDE → circle passes below → choose SE
```

**Update formulas (the key insight — incremental computation):**
```
If chose E:    p_new = p + 2*x + 3          (simplifies to 4x+6 with scaling)
If chose SE:   p_new = p + 2*(x-y) + 5      (simplifies to 4(x-y)+10)
```

The Java code uses the scaled versions `4*x + 6` and `4*(x-y) + 10`.

---

## Worked Example: Trace Table

**Circle with radius r = 10:**

```
Initial: x=0, y=10, p = 3 - 2*10 = -17
```

| Step | x | y | p (before) | Decision | p (after) |
|------|---|---|------------|----------|-----------|
| 0    | 0 | 10| -17        |          |           |
| 1    | 1 | 10| -17 < 0   | E (stay) | -17+4(0)+6 = -11 |
| 2    | 2 | 10| -11 < 0   | E        | -11+4(1)+6 = -1  |
| 3    | 3 | 10| -1 < 0    | E        | -1+4(2)+6 = 13   |
| 4    | 4 | 9 | 13 ≥ 0    | SE (dec y)| 13+4(3-10)+10 = -5 |
| 5    | 5 | 9 | -5 < 0    | E        | -5+4(4)+6 = 17   |
| 6    | 6 | 8 | 17 ≥ 0    | SE       | 17+4(5-9)+10 = 11 |
| 7    | 7 | 7 | 11 ≥ 0    | SE       | 11+4(6-8)+10 = 13 |

**Stop:** x (7) ≤ y (7), but next step x=8 > y=7 → done.

Total: 8 steps × 8 symmetric points = 64 pixels for the circle!

---

## Visual: The Octant We Compute

```
We only compute the arc from 12 o'clock to 1:30 (0° to 45°):

         y
    10 ┤  ●  ← start (0, 10)
     9 ┤  ● ●  ← stays at y=10, then drops to y=9
     8 ┤      ●
     7 ┤        ● ← end (x=y, the 45° line)
       ├──┼──┼──┼──┤
       0  2  4  6  8   x

The 8-way symmetry mirrors this to all other octants.
```

---

## Exercises

### Exercise 1: Trace a Circle
Trace the algorithm for **r = 8**:
- Initial p = 3 - 16 = -13
- Fill in the trace table until x > y
- Count total pixels (steps × 8)
- Run the program and verify with octant colouring

### Exercise 2: Concentric Circles
Draw concentric circles at the same centre with radii 20, 40, 60, 80, 100:

```python
for r in [20, 40, 60, 80, 100]:
    points = bresenham_circle(400, 300, r)
    for px, py, _ in points:
        plot_pixel(screen, px, py)
```

### Exercise 3: Quarter Circle
Modify `plot_circle_points` to only draw the **top-right quarter** (octants 1 and 5 only). This demonstrates that each octant is independent.

```python
def plot_quarter_circle(xc, yc, x, y):
    return [
        (xc + x, yc - y),  # top-right, octant 1
        (xc + y, yc - x),  # top-right, octant 2
    ]
```

### Exercise 4: Filled Circle
The program has a filled mode (press F). Study how it works:
- For each (x, y) pair, draw a horizontal line from `(xc-x)` to `(xc+x)` at height `yc±y`
- This fills the circle using scan lines

Implement your own filled circle from scratch:
```python
def filled_circle(xc, yc, r):
    """Return list of (x1, y, x2, y) horizontal line segments."""
    # Hint: use bresenham_circle but draw horizontal lines
    # between each pair of symmetric points
    pass
```

### Exercise 5: Compare with Trigonometric Circle
Draw a circle using `sin`/`cos` and compare with Bresenham:

```python
import math
def trig_circle(xc, yc, r, num_points=360):
    points = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        x = int(xc + r * math.cos(angle))
        y = int(yc + r * math.sin(angle))
        points.append((x, y))
    return points
```

Questions to answer:
- Which method produces fewer gaps?
- Which is faster for the same radius?
- What happens to the trig method with very large radii?

---

## Common Student Questions

**Q: Why does the loop stop at x ≤ y?**
A: At x = y, we've reached the 45° line. Beyond that, we'd be computing the same octant again (symmetry would duplicate pixels). The 8 symmetric mirrors handle everything past 45°.

**Q: Why is the initial p = 3 - 2*r and not something else?**
A: It comes from evaluating F(1, r-0.5) — the midpoint after the very first step from (0, r). The "3" comes from `1² + (r-0.5)² - r² = 1 + r² - r + 0.25 - r² = 1.25 - r`, scaled by 4 and rounded.

**Q: The Java uses `do...while` but the Python uses `while`. Does it matter?**
A: We plot the initial point (0, r) before the loop in the Python version. The Java `do...while` plots after the first decision. Both produce the same circle; the order of the first pixel differs slightly.

**Q: Can I draw an oval/ellipse with this algorithm?**
A: Not directly — ellipses don't have 8-way symmetry (only 4-way). The midpoint ellipse algorithm handles that (a potential future tutorial).

---

## Key Takeaways

| Concept | What to Remember |
|---------|-----------------|
| **8-way symmetry** | Compute 1 octant, mirror to get all 8 |
| **Decision parameter** | `p = 3 - 2*r` initially |
| **p < 0** | Midpoint inside circle → go East (keep y) |
| **p ≥ 0** | Midpoint outside → go South-East (decrease y) |
| **Loop condition** | `while x ≤ y` (stop at 45°) |
| **Integer only** | No sin/cos, no floating-point |

---

## What's Next

The next tutorial applies 2D transformation matrices — specifically **rotation** — to geometric shapes. This is the foundation for all animation and camera control in computer graphics.
