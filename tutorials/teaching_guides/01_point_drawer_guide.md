# Tutorial 01: Point Drawer — Teaching Guide

## Overview
This tutorial introduces the **most fundamental operation** in computer graphics: plotting a single point (pixel) on the screen. Every line, circle, and complex shape is ultimately just a collection of individual points. Understanding coordinate systems and pixel plotting is the essential foundation.

**Based on**: `PointDrawer.java`

---

## Prerequisites and Setup

```powershell
cd tutorials\lineDrawing
python 01_point_drawer.py
```

**Expected Output:** A white window with a red dot at Cartesian position (100, 300). Click anywhere to add more points.

**Controls:**
- **Click** — Plot a point
- **C** — Clear all points
- **ESC** — Exit

---

## Learning Objectives

By the end of this tutorial, students will understand:
1. The difference between **screen coordinates** and **Cartesian coordinates**
2. How to plot a pixel at a specific location
3. The concept of a **framebuffer** — the grid of pixels that forms your display
4. The basic structure of a graphics application (init → loop → draw → handle events)

---

## The Two Coordinate Systems

### Screen Coordinates (Pygame/Java default)
```
(0,0)────────────→ X
  │
  │   Origin at TOP-LEFT
  │   Y increases DOWNWARD
  │
  ↓ Y
```

### Cartesian Coordinates (Mathematics)
```
  ↑ Y
  │
  │   Origin at BOTTOM-LEFT
  │   Y increases UPWARD
  │
(0,0)────────────→ X
```

### Conversion Formula
```python
# Screen → Cartesian
cart_y = screen_height - screen_y

# Cartesian → Screen  
screen_y = screen_height - cart_y
```

This is why the Java code has:
```java
int drawY = getHeight() - (int) Math.round(point.getY()) - pointSize / 2;
```

---

## Code Breakdown

### 1. The Core Operation: Plotting a Point

**Java original:**
```java
g.setColor(Color.RED);
g.fillOval(drawX, drawY, pointSize, pointSize);
```

**Python equivalent:**
```python
def draw_point(surface, x, y, color=POINT_COLOR, size=POINT_SIZE):
    sx, sy = cartesian_to_screen(x, y, surface.get_height())
    pygame.draw.circle(surface, color, (int(sx), int(sy)), size // 2)
```

**What's happening:**
1. Convert from Cartesian coordinates (math-friendly) to screen coordinates (display-friendly)
2. Draw a small filled circle at that position
3. The `size // 2` is the radius (Java's `fillOval` takes width/height, Pygame's `circle` takes radius)

---

### 2. The Application Loop

Every graphics program follows this pattern:

```
┌─────────────────────────────────┐
│         Initialize              │
│  (create window, set up state)  │
└──────────┬──────────────────────┘
           ↓
┌─────────────────────────────────┐
│      Main Loop (60 FPS)         │←──┐
│                                 │   │
│  1. Handle events (keyboard,    │   │
│     mouse clicks, quit)         │   │
│                                 │   │
│  2. Clear screen                │   │
│                                 │   │
│  3. Draw everything             │   │
│                                 │   │
│  4. Flip (show the frame)       │   │
│                                 │   │
└──────────┬──────────────────────┘   │
           └──────────────────────────┘
```

### 3. Java vs Python Comparison

| Aspect | Java (PointDrawer.java) | Python (01_point_drawer.py) |
|--------|-------------------------|---------------------------|
| Window | `JFrame` + `JPanel` | `pygame.display.set_mode()` |
| Drawing | `Graphics g` in `paintComponent()` | `screen` surface in main loop |
| Plot point | `g.fillOval(x, y, w, h)` | `pygame.draw.circle(surface, ...)` |
| Coordinate flip | Manual in `paintComponent` | `cartesian_to_screen()` function |
| Event loop | Swing's internal loop | Explicit `while running` loop |

---

## What is a Pixel?

A pixel (picture element) is the smallest addressable unit on a screen.

```
Screen = a grid of pixels:
┌───┬───┬───┬───┬───┬───┬───┐
│   │   │   │   │   │   │   │
├───┼───┼───┼───┼───┼───┼───┤
│   │   │   │ ● │   │   │   │  ← One pixel at (3,1)
├───┼───┼───┼───┼───┼───┼───┤
│   │   │   │   │   │   │   │
├───┼───┼───┼───┼───┼───┼───┤
│   │   │   │   │   │   │   │
└───┴───┴───┴───┴───┴───┴───┘
```

Resolution 1920×1080 = 2,073,600 individual pixels to colour every frame!

---

## Exercises

### Exercise 1: Plot Specific Points
Plot points at these Cartesian coordinates and verify they appear in the correct positions:
- (0, 0) — bottom-left corner
- (400, 300) — centre of window
- (799, 599) — top-right corner

```python
points = [(0, 0), (400, 300), (799, 599)]
```

### Exercise 2: Draw a Plus Sign (+)
Plot 5 points to form a plus sign centred at (400, 300):
```python
# Hint: centre point + 4 points at equal distance in each direction
centre = (400, 300)
offset = 20
points = [
    centre,
    (centre[0] + offset, centre[1]),  # right
    (centre[0] - offset, centre[1]),  # left
    (centre[0], centre[1] + offset),  # up
    (centre[0], centre[1] - offset),  # down
]
```

### Exercise 3: Draw a Square Using Points
Plot points at equal intervals along the edges of a square from (200,200) to (400,400):

```python
def draw_square_points(x1, y1, x2, y2, spacing=5):
    """Return a list of points forming a square outline."""
    points = []
    # Top edge
    for x in range(x1, x2 + 1, spacing):
        points.append((x, y2))
    # Bottom edge
    for x in range(x1, x2 + 1, spacing):
        points.append((x, y1))
    # Left edge
    for y in range(y1, y2 + 1, spacing):
        points.append((x1, y))
    # Right edge
    for y in range(y1, y2 + 1, spacing):
        points.append((x2, y))
    return points
```

### Exercise 4: Coordinate System Verification
Modify the program to display BOTH coordinate systems simultaneously:
- Show the screen coordinate under the mouse cursor
- Show the equivalent Cartesian coordinate
- This reinforces the Y-axis flip concept

### Exercise 5: Pixel Art
Draw a simple 8×8 pixel art character (like a smiley face) by plotting individual points:
```python
# Each 1 represents a plotted pixel
smiley = [
    [0,0,1,1,1,1,0,0],
    [0,1,0,0,0,0,1,0],
    [1,0,1,0,0,1,0,1],
    [1,0,0,0,0,0,0,1],
    [1,0,1,0,0,1,0,1],
    [1,0,0,1,1,0,0,1],
    [0,1,0,0,0,0,1,0],
    [0,0,1,1,1,1,0,0],
]
```

---

## Common Student Questions

**Q: Why don't we just use `pygame.draw.line` or other built-in shapes?**
A: We could! But in computer graphics, we need to understand *how* those functions work internally. Every `draw.line` call is ultimately plotting individual pixels — we're learning the foundation.

**Q: Why bother with two coordinate systems?**
A: Mathematics uses bottom-left origin (Cartesian), but hardware framebuffers use top-left origin (screen). Understanding the conversion prevents endless "my shape is upside down" bugs.

**Q: Is `set_at()` the fastest way to plot pixels in Pygame?**
A: No — for performance, you'd use `pygame.surfarray` to write directly to a numpy array backing the surface. But `set_at()` is clearest for learning.

---

## Key Takeaways

| Concept | What to Remember |
|---------|-----------------|
| **Pixel** | Smallest addressable point on screen |
| **Screen coords** | Origin at top-left, Y goes down |
| **Cartesian coords** | Origin at bottom-left, Y goes up |
| **Coordinate conversion** | `screen_y = height - cart_y` |
| **Game loop** | Init → (Events → Update → Draw → Flip) → Quit |

---

## What's Next

Now that we can plot individual points, the next tutorial asks: **how do we efficiently decide WHICH points to plot to draw a straight line between two endpoints?** That's the Bresenham Line Algorithm.
