# Cartesian Plane, Point Drawing, and DDA Line Drawing

## 1. Why This Topic Matters

In computer graphics, every shape is made from pixels.
A line is not drawn as one perfect math object on screen.
It is drawn as many small points (pixels).

---

## 2. Cartesian Plane Basics

A Cartesian plane has:
- X-axis (horizontal)
- Y-axis (vertical)
- Origin at (0, 0)

### The 4 regions (quadrants)

1. Quadrant I: x > 0, y > 0 (top-right)
2. Quadrant II: x < 0, y > 0 (top-left)
3. Quadrant III: x < 0, y < 0 (bottom-left)
4. Quadrant IV: x > 0, y < 0 (bottom-right)

Quick sign table:

| Quadrant | x sign | y sign |
|---|---|---|
| I | + | + |
| II | - | + |
| III | - | - |
| IV | + | - |

---

## 3. Cartesian vs Screen Coordinates

Math class (Cartesian):
- Origin is at center (in this tutorial)
- y goes upward

Screen (Pygame):
- Origin is top-left corner of the window
- y goes downward

So we convert coordinates:

- Screen to Cartesian:
  - `cx = sx - width/2`
  - `cy = height/2 - sy`

- Cartesian to Screen:
  - `sx = width/2 + cx`
  - `sy = height/2 - cy`

These are used in both files so students can think in normal math coordinates.

---


### What this file 

1. Draw a grid and axes for reference.
2. Convert mouse click from screen space to Cartesian space.
3. Plot points and show coordinate labels.
4. Store points in a list and redraw each frame.

### Controls

- Mouse click: plot point
- C: clear all points
- ESC: quit

---

## 5. Part B: DDA Line Drawing 

## What is DDA?

DDA means Digital Differential Analyzer.
It draws a line by moving in very small equal steps from start point to end point.

### Core formulas

Given two points `(x0, y0)` and `(x1, y1)`:

- `dx = x1 - x0`
- `dy = y1 - y0`
- `steps = max(abs(dx), abs(dy))`
- `x_inc = dx / steps`
- `y_inc = dy / steps`

Then:

1. Start from `(x, y) = (x0, y0)`
2. Plot `round(x), round(y)`
3. Add increments each step

### Why `max(abs(dx), abs(dy))`?

Because we need enough steps in the dominant direction.
This avoids gaps in steep lines.

### Special case

If start point = end point, plot one pixel only.

---

## 6. Simple Example 

Line from `(2, 1)` to `(8, 4)`:

- `dx = 6`
- `dy = 3`
- `steps = 6`
- `x_inc = 1`
- `y_inc = 0.5`

Generated float points:
- (2.0, 1.0)
- (3.0, 1.5)
- (4.0, 2.0)
- (5.0, 2.5)
- (6.0, 3.0)
- (7.0, 3.5)
- (8.0, 4.0)

After rounding:
- (2,1), (3,2), (4,2), (5,2), (6,3), (7,4), (8,4)

This is the pixel line shown on screen.

---

## 7. Controls in DDA 

- Click 2 points: draw line
- I: input mode (type points)
- Enter: draw typed line
- D: debug mode on/off
- SPACE: next debug step
- C: clear all
- ESC: quit

---

## 8. Why Debug Mode Is Great 

The debug mode in `DDA_line_draw.py` shows:
- `dx`, `dy`, `steps`
- `x_inc`, `y_inc`
- current float `(x, y)`
- rounded pixel at each step
---


## Quick Practice Questions

1. In which quadrant is point `(-5, 7)`?
2. In which quadrant is point `(4, -3)`?
3. For line `(1,1)` to `(5,3)`, find `dx`, `dy`, `steps`.
4. Why do we round `(x, y)` in DDA?

Answers:
1. Quadrant II
2. Quadrant IV
3. `dx=4`, `dy=2`, `steps=4`
4. Because screen pixels are integer locations.

---

## Key Takeaway

- Cartesian plane helps students reason with math.
- Point plotting is the base of all raster graphics.
- DDA is an easy first line algorithm for learning pixel-based drawing.
