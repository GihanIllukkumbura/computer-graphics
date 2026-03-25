"""
Tutorial 02: Bresenham's Line Algorithm
========================================
Based on: Bresenhams.java

Demonstrates Bresenham's line-drawing algorithm — an efficient method
that uses ONLY integer arithmetic to determine which pixels to plot.

The key idea: a "decision parameter" p decides whether the next pixel
should go straight (only increment x) or diagonally (increment both x and y).

This implementation handles ALL 8 octants (any slope, any direction).

Controls:
    - Click two points to draw a line
    - R = Reset
    - D = Toggle step-by-step debug mode
    - SPACE = Next step (in debug mode)
    - ESC = Quit
"""

import pygame
import sys

# ============================================================
# Configuration
# ============================================================
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
PIXEL_SIZE = 1           # Set to >1 for "zoomed" pixel view
BG_COLOR = (255, 255, 255)
LINE_COLOR = (0, 0, 200)
POINT_COLOR = (255, 0, 0)
GRID_COLOR = (230, 230, 230)
TEXT_COLOR = (0, 0, 0)
HIGHLIGHT_COLOR = (255, 200, 0)


def screen_to_cartesian(sx, sy):
    """Convert screen coordinates (top-left origin) to Cartesian (center origin)."""
    return sx - WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - sy


def cartesian_to_screen(cx, cy):
    """Convert Cartesian coordinates (center origin) to screen (top-left origin)."""
    return WINDOW_WIDTH // 2 + cx, WINDOW_HEIGHT // 2 - cy


def plot_pixel(surface, x, y, color=LINE_COLOR, size=PIXEL_SIZE):
    """Plot a single pixel at Cartesian coordinates (x, y)."""
    sx, sy = cartesian_to_screen(x, y)

    if size <= 1:
        if 0 <= sx < surface.get_width() and 0 <= sy < surface.get_height():
            surface.set_at((int(sx), int(sy)), color)
    else:
        pygame.draw.rect(surface, color,
                         (int(sx) - size // 2, int(sy) - size // 2, size, size))


def draw_axes(surface):
    """Draw X and Y axes crossing at origin (0,0)."""
    w, h = surface.get_size()
    cx, cy = w // 2, h // 2
    pygame.draw.line(surface, GRID_COLOR, (0, cy), (w, cy), 1)
    pygame.draw.line(surface, GRID_COLOR, (cx, 0), (cx, h), 1)


def draw_point_label(surface, font, x, y, color=TEXT_COLOR):
    """Draw coordinate text near a Cartesian point."""
    sx, sy = cartesian_to_screen(x, y)
    label = font.render(f"({x}, {y})", True, color)
    surface.blit(label, (int(sx) + 8, int(sy) - 18))


def bresenham_line(x1, y1, x2, y2):
    """
    Bresenham's line algorithm — returns list of (x, y) pixel coordinates.

    Direct translation of the Java reference code, extended to handle
    all 8 octants (the original Java only handles octant 1).

    Original Java logic (octant 1 only):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        p = 2 * dy - dx
        for k in range(dx):
            if p < 0:
                x += 1
                p = p + 2 * dy
            else:
                x += 1; y += 1
                p = p + 2 * (dy - dx)
    """
    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    # Determine step direction for x and y
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    x, y = x1, y1
    points.append((x, y))

    if dx >= dy:
        # Gentle slope (|slope| <= 1): step in x
        # This matches the original Java code's logic
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
        # Steep slope (|slope| > 1): step in y
        # Swap roles of x and y
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


def bresenham_line_with_trace(x1, y1, x2, y2):
    """
    Same as bresenham_line but also returns trace info for each step:
    [(x, y, p_value, decision), ...]

    Useful for teaching — students can see the decision parameter evolve.
    """
    trace = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    x, y = x1, y1
    
    if dx >= dy:
        p = 2 * dy - dx
        trace.append((x, y, p, "start"))
        for k in range(dx):
            old_p = p
            if p < 0:
                x += sx
                p = p + (2 * dy)
                trace.append((x, y, p, f"p={old_p}<0 → move x only"))
            else:
                x += sx
                y += sy
                p = p + (2 * (dy - dx))
                trace.append((x, y, p, f"p={old_p}>=0 → move x AND y"))
    else:
        p = 2 * dx - dy
        trace.append((x, y, p, "start"))
        for k in range(dy):
            old_p = p
            if p < 0:
                y += sy
                p = p + (2 * dx)
                trace.append((x, y, p, f"p={old_p}<0 → move y only"))
            else:
                y += sy
                x += sx
                p = p + (2 * (dx - dy))
                trace.append((x, y, p, f"p={old_p}>=0 → move x AND y"))

    return trace


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tutorial 02: Bresenham's Line Algorithm")
    font = pygame.font.SysFont("Consolas", 15)
    clock = pygame.time.Clock()

    click_points = []   # Stores clicked endpoints
    drawn_lines = []    # List of line pixel lists
    debug_mode = False
    debug_trace = []
    debug_step = 0
    debug_points = None

    # Pre-draw an example line in Cartesian coordinates.
    p1_example, p2_example = (100, 100), (400, 200)
    example_pixels = bresenham_line(p1_example[0], p1_example[1], p2_example[0], p2_example[1])
    drawn_lines.append(("Example: (100,100)→(400,200)", example_pixels, (0, 150, 0), p1_example, p2_example))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    click_points.clear()
                    drawn_lines.clear()
                    debug_trace.clear()
                    debug_step = 0
                    debug_points = None
                elif event.key == pygame.K_d:
                    debug_mode = not debug_mode
                elif event.key == pygame.K_SPACE and debug_mode and debug_trace:
                    debug_step = min(debug_step + 1, len(debug_trace) - 1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                click_points.append(screen_to_cartesian(mx, my))
                if len(click_points) == 2:
                    p1, p2 = click_points
                    if debug_mode:
                        debug_trace = bresenham_line_with_trace(
                            p1[0], p1[1], p2[0], p2[1])
                        debug_step = 0
                        debug_points = (p1, p2)
                    else:
                        pixels = bresenham_line(
                            p1[0], p1[1], p2[0], p2[1])
                        label = f"({p1[0]},{p1[1]})→({p2[0]},{p2[1]})"
                        drawn_lines.append((label, pixels, LINE_COLOR, p1, p2))
                    click_points.clear()

        # --- Drawing ---
        screen.fill(BG_COLOR)
        draw_axes(screen)

        # Draw all completed lines
        for label, pixels, color, p1, p2 in drawn_lines:
            for px, py in pixels:
                plot_pixel(screen, px, py, color)
            draw_point_label(screen, font, p1[0], p1[1], (120, 0, 0))
            draw_point_label(screen, font, p2[0], p2[1], (120, 0, 0))

        # Draw debug trace (step-by-step)
        if debug_mode and debug_trace:
            for i in range(min(debug_step + 1, len(debug_trace))):
                tx, ty, tp, tdesc = debug_trace[i]
                c = HIGHLIGHT_COLOR if i == debug_step else LINE_COLOR
                plot_pixel(screen, tx, ty, c, max(PIXEL_SIZE, 5))

            # Keep endpoints visible and labeled while stepping through debug trace.
            if debug_points is not None:
                p1, p2 = debug_points
                plot_pixel(screen, p1[0], p1[1], POINT_COLOR, 7)
                plot_pixel(screen, p2[0], p2[1], POINT_COLOR, 7)
                draw_point_label(screen, font, p1[0], p1[1], POINT_COLOR)
                draw_point_label(screen, font, p2[0], p2[1], POINT_COLOR)

            # Show trace info
            if debug_step < len(debug_trace):
                info = debug_trace[debug_step]
                info_text = font.render(
                    f"Step {debug_step}: ({info[0]},{info[1]})  p={info[2]}  {info[3]}",
                    True, TEXT_COLOR)
                screen.blit(info_text, (10, WINDOW_HEIGHT - 60))
                progress = font.render(
                    f"SPACE=next step | Step {debug_step+1}/{len(debug_trace)}",
                    True, (150, 0, 0))
                screen.blit(progress, (10, WINDOW_HEIGHT - 35))

            if debug_points is not None:
                p1, p2 = debug_points
                debug_points_text = font.render(
                    f"Debug endpoints: P1({p1[0]}, {p1[1]}), P2({p2[0]}, {p2[1]})",
                    True, TEXT_COLOR)
                screen.blit(debug_points_text, (10, WINDOW_HEIGHT - 85))

        # Draw click markers
        for cp in click_points:
            plot_pixel(screen, cp[0], cp[1], POINT_COLOR, 7)
            draw_point_label(screen, font, cp[0], cp[1], POINT_COLOR)

        # HUD
        mode_str = "[DEBUG MODE] " if debug_mode else ""
        title = font.render(
            f"{mode_str}Bresenham's Line — Click 2 points | R=Reset | D=Debug | ESC=Quit",
            True, TEXT_COLOR)
        screen.blit(title, (10, 10))

        if len(click_points) == 1:
            hint = font.render("Click second point...", True, POINT_COLOR)
            screen.blit(hint, (10, 32))

        origin_text = font.render("Origin: (0, 0)", True, TEXT_COLOR)
        screen.blit(origin_text, (10, 54))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
