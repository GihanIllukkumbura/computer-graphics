"""
Tutorial 03: Bresenham's Circle Algorithm
==========================================
Based on: BresenhamsCircle.java

Demonstrates the Midpoint Circle algorithm — uses integer arithmetic
and 8-way symmetry to efficiently draw circles.

The key insight: you only need to compute pixels for 1/8 of the circle
(one octant from 0° to 45°), then mirror them to get the full circle.

Decision parameter:
    p = 3 - 2*r     (initial)
    if p < 0:  p = p + 4*x + 6
    else:      p = p + 4*(x - y) + 10;  y -= 1

Controls:
    - Click to set centre, then click again to set radius
    - R = Reset
    - F = Toggle filled circle mode
    - ESC = Quit
"""

import pygame
import sys
import math

# ============================================================
# Configuration
# ============================================================
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BG_COLOR = (255, 255, 255)
CIRCLE_COLOR = (0, 0, 200)
CENTER_COLOR = (255, 0, 0)
TEXT_COLOR = (0, 0, 0)
OCTANT_COLORS = [
    (255, 0, 0),       # Octant 1 - Red
    (0, 200, 0),       # Octant 2 - Green
    (0, 0, 255),       # Octant 3 - Blue
    (255, 165, 0),     # Octant 4 - Orange
    (128, 0, 128),     # Octant 5 - Purple
    (0, 200, 200),     # Octant 6 - Cyan
    (200, 200, 0),     # Octant 7 - Yellow
    (255, 105, 180),   # Octant 8 - Pink
]


def plot_circle_points(xc, yc, x, y, colored=False):
    """
    Plot 8 symmetric points for a circle centred at (xc, yc).

    This is a direct translation of the Java:
        g.drawLine(xc + x, yc + y, xc + x, yc + y);  // point
        g.drawLine(xc + x, yc - y, xc + x, yc - y);
        g.drawLine(xc - x, yc + y, xc - x, yc + y);
        g.drawLine(xc - x, yc - y, xc - x, yc - y);
        g.drawLine(xc + y, yc + x, xc + y, yc + x);
        g.drawLine(xc + y, yc - x, xc + y, yc - x);
        g.drawLine(xc - y, yc + x, xc - y, yc + x);
        g.drawLine(xc - y, yc - x, xc - y, yc - x);

    Returns list of (x, y, color_index) tuples.
    """
    return [
        (xc + x, yc + y, 0),   # Octant 1
        (xc + x, yc - y, 1),   # Octant 2
        (xc - x, yc + y, 2),   # Octant 3
        (xc - x, yc - y, 3),   # Octant 4
        (xc + y, yc + x, 4),   # Octant 5
        (xc + y, yc - x, 5),   # Octant 6
        (xc - y, yc + x, 6),   # Octant 7
        (xc - y, yc - x, 7),   # Octant 8
    ]


def bresenham_circle(xc, yc, r):
    """
    Bresenham's circle algorithm.
    Direct translation of BresenhamsCircle.java.

    Returns list of (x, y, octant_index) for all plotted pixels.
    """
    points = []
    x = 0
    y = r
    p = 3 - (2 * r)

    # Plot initial points at (0, r) — the 4 cardinal points
    points.extend(plot_circle_points(xc, yc, x, y))

    while x <= y:
        if p < 0:
            p = p + (4 * x) + 6
        else:
            p = p + (4 * (x - y)) + 10
            y = y - 1
        x = x + 1
        points.extend(plot_circle_points(xc, yc, x, y))

    return points


def bresenham_circle_with_trace(xc, yc, r):
    """
    Same as bresenham_circle but returns trace info for teaching.
    Each entry: (x_offset, y_offset, p_value, decision_text)
    Plus the full points list.
    """
    trace = []
    all_points = []

    x = 0
    y = r
    p = 3 - (2 * r)

    all_points.extend(plot_circle_points(xc, yc, x, y))
    trace.append((x, y, p, "initial"))

    while x <= y:
        old_p = p
        if p < 0:
            p = p + (4 * x) + 6
            decision = f"p={old_p}<0 → y stays"
        else:
            p = p + (4 * (x - y)) + 10
            y = y - 1
            decision = f"p={old_p}>=0 → y decreases"
        x = x + 1
        all_points.extend(plot_circle_points(xc, yc, x, y))
        trace.append((x, y, p, decision))

    return all_points, trace


def bresenham_circle_filled(xc, yc, r):
    """Draw a filled circle using horizontal scan lines between symmetric points."""
    lines = []
    x = 0
    y = r
    p = 3 - (2 * r)

    def add_fill_lines(xc, yc, x, y):
        lines.append((xc - x, yc + y, xc + x, yc + y))
        lines.append((xc - x, yc - y, xc + x, yc - y))
        lines.append((xc - y, yc + x, xc + y, yc + x))
        lines.append((xc - y, yc - x, xc + y, yc - x))

    add_fill_lines(xc, yc, x, y)

    while x <= y:
        if p < 0:
            p = p + (4 * x) + 6
        else:
            p = p + (4 * (x - y)) + 10
            y -= 1
        x += 1
        add_fill_lines(xc, yc, x, y)

    return lines


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tutorial 03: Bresenham's Circle Algorithm")
    font = pygame.font.SysFont("Consolas", 15)
    clock = pygame.time.Clock()

    circles = []        # List of (xc, yc, r, points)
    click_center = None
    show_octants = True  # Color each octant differently
    filled_mode = False

    # Pre-draw the example from the Java reference: centre(300,300), r=200
    example_points = bresenham_circle(300, 300, 200)
    circles.append((300, 300, 200, example_points))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    circles.clear()
                    click_center = None
                elif event.key == pygame.K_o:
                    show_octants = not show_octants
                elif event.key == pygame.K_f:
                    filled_mode = not filled_mode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if click_center is None:
                    click_center = (mx, my)
                else:
                    # Calculate radius from distance
                    dx = mx - click_center[0]
                    dy = my - click_center[1]
                    r = int(math.sqrt(dx*dx + dy*dy))
                    if r > 0:
                        points = bresenham_circle(click_center[0], click_center[1], r)
                        circles.append((click_center[0], click_center[1], r, points))
                    click_center = None

        # --- Drawing ---
        screen.fill(BG_COLOR)

        # Draw all circles
        for xc, yc, r, points in circles:
            if filled_mode:
                fill_lines = bresenham_circle_filled(xc, yc, r)
                for lx1, ly1, lx2, ly2 in fill_lines:
                    pygame.draw.line(screen, (200, 200, 255), (lx1, ly1), (lx2, ly2))

            for px, py, octant in points:
                if 0 <= px < WINDOW_WIDTH and 0 <= py < WINDOW_HEIGHT:
                    color = OCTANT_COLORS[octant] if show_octants else CIRCLE_COLOR
                    screen.set_at((px, py), color)

            # Mark centre
            pygame.draw.circle(screen, CENTER_COLOR, (xc, yc), 3)

        # Draw click marker and preview
        if click_center:
            pygame.draw.circle(screen, CENTER_COLOR, click_center, 4)
            mx, my = pygame.mouse.get_pos()
            dx = mx - click_center[0]
            dy = my - click_center[1]
            preview_r = int(math.sqrt(dx*dx + dy*dy))
            if preview_r > 0:
                pygame.draw.circle(screen, (200, 200, 200), click_center, preview_r, 1)

        # HUD
        mode_str = "[FILLED] " if filled_mode else ""
        title = font.render(
            f"{mode_str}Bresenham's Circle — Click centre, then set radius | O=Octant colors | F=Fill | R=Reset | ESC=Quit",
            True, TEXT_COLOR)
        screen.blit(title, (10, 10))

        if click_center:
            hint = font.render(
                f"Centre set at {click_center}. Click to set radius...", True, CENTER_COLOR)
            screen.blit(hint, (10, 32))

        if show_octants:
            for i, label in enumerate(["Oct1", "Oct2", "Oct3", "Oct4", "Oct5", "Oct6", "Oct7", "Oct8"]):
                c = OCTANT_COLORS[i]
                pygame.draw.rect(screen, c, (WINDOW_WIDTH - 110, 10 + i * 18, 12, 12))
                t = font.render(label, True, TEXT_COLOR)
                screen.blit(t, (WINDOW_WIDTH - 92, 8 + i * 18))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
