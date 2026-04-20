"""
Tutorial: Bresenham Line Drawing Algorithm
==========================================
Based on: Bresenhams.java

Demonstrates Bresenham's line-drawing algorithm — an efficient method
that uses ONLY integer arithmetic to determine which pixels to plot.

The key idea: a "decision parameter" p decides whether the next pixel
should go straight (only increment x) or diagonally (increment both x and y).

This implementation handles ALL 8 octants (any slope, any direction).

Controls:
    - Click two points to draw a line
    - I = Toggle typed-input mode
    - Enter = Draw using typed points
    - D = Toggle debug mode
    - SPACE = Next step (in debug mode)
    - C = Clear all drawn lines
    - ESC = Quit
"""

import pygame
import sys

# ============================================================
# Configuration
# ============================================================
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
PIXEL_SIZE = 2
BG_COLOR = (255, 255, 255)
GRID_COLOR = (238, 238, 238)
AXIS_COLOR = (205, 205, 205)
TEXT_COLOR = (0, 0, 0)
LINE_COLOR = (0, 90, 200)
POINT_COLOR = (220, 30, 30)
EXAMPLE_COLOR = (0, 140, 80)
HIGHLIGHT_COLOR = (255, 180, 0)
DEBUG_TEXT_COLOR = (20, 20, 20)


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


def draw_grid(surface, spacing=50):
    """Draw a light background grid."""
    w, h = surface.get_size()
    cx, cy = w // 2, h // 2

    for x in range(cx % spacing, w, spacing):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, h), 1)
    for y in range(cy % spacing, h, spacing):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (w, y), 1)


def draw_axes(surface):
    """Draw x and y axes crossing at origin."""
    w, h = surface.get_size()
    cx, cy = w // 2, h // 2
    pygame.draw.line(surface, AXIS_COLOR, (0, cy), (w, cy), 1)
    pygame.draw.line(surface, AXIS_COLOR, (cx, 0), (cx, h), 1)


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
    Same as bresenham_line but also returns trace info for each step and metadata.
    
    Returns:
        trace: list of per-step dictionaries
        meta:  dictionary with dx, dy, steps, initial_p
    """
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    x, y = x1, y1
    trace = []
    
    if dx >= dy:
        p = 2 * dy - dx
        initial_p = p
        trace.append({
            "step": 0,
            "x": x,
            "y": y,
            "p": p,
            "decision": "start"
        })
        for step in range(1, dx + 1):
            old_p = p
            if p < 0:
                x += sx
                p = p + (2 * dy)
                decision = f"p={old_p}<0 → move x only"
            else:
                x += sx
                y += sy
                p = p + (2 * (dy - dx))
                decision = f"p={old_p}>=0 → move x AND y"
            trace.append({
                "step": step,
                "x": x,
                "y": y,
                "p": p,
                "decision": decision
            })
        meta = {
            "dx": dx,
            "dy": dy,
            "steps": dx,
            "initial_p": initial_p,
            "mode": "gentle slope (dx >= dy)"
        }
    else:
        p = 2 * dx - dy
        initial_p = p
        trace.append({
            "step": 0,
            "x": x,
            "y": y,
            "p": p,
            "decision": "start"
        })
        for step in range(1, dy + 1):
            old_p = p
            if p < 0:
                y += sy
                p = p + (2 * dx)
                decision = f"p={old_p}<0 → move y only"
            else:
                y += sy
                x += sx
                p = p + (2 * (dx - dy))
                decision = f"p={old_p}>=0 → move x AND y"
            trace.append({
                "step": step,
                "x": x,
                "y": y,
                "p": p,
                "decision": decision
            })
        meta = {
            "dx": dx,
            "dy": dy,
            "steps": dy,
            "initial_p": initial_p,
            "mode": "steep slope (dy > dx)"
        }

    return trace, meta


def parse_typed_points(input_text):
    """Parse typed coordinates and return two points as integers."""
    cleaned = input_text.replace(",", " ").strip()
    parts = [p for p in cleaned.split() if p]
    if len(parts) != 4:
        raise ValueError("Use format: x0 y0 x1 y1 or x0,y0 x1,y1")

    x0, y0, x1, y1 = map(int, parts)
    return (x0, y0), (x1, y1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Bresenham Line Drawing Tutorial")
    font = pygame.font.SysFont("Consolas", 15)
    clock = pygame.time.Clock()

    click_points = []
    drawn_lines = []
    debug_mode = False
    debug_trace = []
    debug_meta = None
    debug_points = None
    debug_step = 0
    input_mode = False
    input_buffer = ""
    input_error = ""

    # Example line visible at startup.
    p1_example = (-200, -100)
    p2_example = (220, 140)
    example_pixels = bresenham_line(p1_example[0], p1_example[1], p2_example[0], p2_example[1])
    drawn_lines.append(("Example", example_pixels, EXAMPLE_COLOR, p1_example, p2_example))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    click_points.clear()
                    drawn_lines.clear()
                    debug_trace.clear()
                    debug_meta = None
                    debug_points = None
                    debug_step = 0
                    input_buffer = ""
                    input_error = "Cleared all lines and inputs."
                elif event.key == pygame.K_i:
                    input_mode = not input_mode
                    input_error = ""
                    if input_mode:
                        click_points.clear()
                elif event.key == pygame.K_d:
                    debug_mode = not debug_mode
                    input_error = "Debug mode ON" if debug_mode else "Debug mode OFF"
                    if not debug_mode:
                        debug_trace.clear()
                        debug_meta = None
                        debug_points = None
                        debug_step = 0
                elif input_mode:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        try:
                            p0, p1 = parse_typed_points(input_buffer)
                            if debug_mode:
                                debug_trace, debug_meta = bresenham_line_with_trace(p0[0], p0[1], p1[0], p1[1])
                                debug_points = (p0, p1)
                                debug_step = 0
                                input_error = "Debug trace loaded from typed points. Press SPACE to step."
                            else:
                                pixels = bresenham_line(p0[0], p0[1], p1[0], p1[1])
                                label = f"({p0[0]},{p0[1]}) -> ({p1[0]},{p1[1]})"
                                drawn_lines.append((label, pixels, LINE_COLOR, p0, p1))
                                input_error = "Line created from typed input."
                        except ValueError as exc:
                            input_error = str(exc)
                    elif event.key == pygame.K_BACKSPACE:
                        input_buffer = input_buffer[:-1]
                    else:
                        # Accept digits, minus sign, comma, and spaces for point input.
                        if event.unicode and event.unicode in "0123456789-, ":
                            input_buffer += event.unicode
                elif event.key == pygame.K_SPACE and debug_mode and debug_trace:
                    debug_step = min(debug_step + 1, len(debug_trace) - 1)
            elif event.type == pygame.MOUSEBUTTONDOWN and not input_mode:
                mx, my = event.pos
                click_points.append(screen_to_cartesian(mx, my))

                if len(click_points) == 2:
                    p0, p1 = click_points
                    if debug_mode:
                        debug_trace, debug_meta = bresenham_line_with_trace(p0[0], p0[1], p1[0], p1[1])
                        debug_points = (p0, p1)
                        debug_step = 0
                    else:
                        pixels = bresenham_line(p0[0], p0[1], p1[0], p1[1])
                        label = f"({p0[0]},{p0[1]}) -> ({p1[0]},{p1[1]})"
                        drawn_lines.append((label, pixels, LINE_COLOR, p0, p1))
                    click_points.clear()

        screen.fill(BG_COLOR)
        draw_grid(screen)
        draw_axes(screen)

        for _, pixels, color, p0, p1 in drawn_lines:
            for px, py in pixels:
                plot_pixel(screen, px, py, color)
            plot_pixel(screen, p0[0], p0[1], POINT_COLOR, 7)
            plot_pixel(screen, p1[0], p1[1], POINT_COLOR, 7)
            draw_point_label(screen, font, p0[0], p0[1], POINT_COLOR)
            draw_point_label(screen, font, p1[0], p1[1], POINT_COLOR)

        if debug_mode and debug_trace:
            for i in range(debug_step + 1):
                step_info = debug_trace[i]
                c = HIGHLIGHT_COLOR if i == debug_step else LINE_COLOR
                s = 8 if i == debug_step else max(PIXEL_SIZE, 4)
                plot_pixel(screen, step_info["x"], step_info["y"], c, s)

            if debug_points is not None:
                p0, p1 = debug_points
                plot_pixel(screen, p0[0], p0[1], POINT_COLOR, 7)
                plot_pixel(screen, p1[0], p1[1], POINT_COLOR, 7)
                draw_point_label(screen, font, p0[0], p0[1], POINT_COLOR)
                draw_point_label(screen, font, p1[0], p1[1], POINT_COLOR)

        hud1 = font.render("Bresenham Line: Click 2 points | I=Input Mode | D=Debug | SPACE=Next | C=Clear | ESC=Quit", True, TEXT_COLOR)
        hud2 = font.render(f"Stored lines: {len(drawn_lines)}", True, TEXT_COLOR)
        screen.blit(hud1, (10, 10))
        screen.blit(hud2, (10, 32))

        mode_text = "Mode: DEBUG" if debug_mode else "Mode: NORMAL"
        input_text = "Input: TYPED" if input_mode else "Input: MOUSE"
        hud3 = font.render(f"{mode_text} | {input_text}", True, DEBUG_TEXT_COLOR)
        screen.blit(hud3, (10, 54))

        if debug_mode and debug_trace and debug_meta is not None:
            current = debug_trace[debug_step]
            debug_line_1 = (
                f"dx={debug_meta['dx']}  dy={debug_meta['dy']}  steps={debug_meta['steps']}  "
                f"mode={debug_meta['mode']}"
            )
            debug_line_2 = (
                f"Step {current['step']}/{debug_meta['steps']}: "
                f"plot({current['x']}, {current['y']})  p={current['p']}"
            )
            debug_line_3 = f"Decision: {current['decision']}"
            screen.blit(font.render(debug_line_1, True, DEBUG_TEXT_COLOR), (10, 76))
            screen.blit(font.render(debug_line_2, True, DEBUG_TEXT_COLOR), (10, 98))
            screen.blit(font.render(debug_line_3, True, DEBUG_TEXT_COLOR), (10, 120))

        if len(click_points) == 1:
            p = click_points[0]
            msg = font.render(f"First point selected: ({p[0]}, {p[1]})", True, TEXT_COLOR)
            screen.blit(msg, (10, 142 if debug_mode and debug_trace else 76))

        if input_mode:
            input_line = f"Typed points: {input_buffer}"
            input_hint = "Enter format: x0 y0 x1 y1   or   x0,y0 x1,y1 | Press Enter to draw"
            screen.blit(font.render(input_hint, True, DEBUG_TEXT_COLOR), (10, WINDOW_HEIGHT - 58))
            screen.blit(font.render(input_line, True, DEBUG_TEXT_COLOR), (10, WINDOW_HEIGHT - 36))
            if input_error:
                status_color = (160, 0, 0) if "format" in input_error.lower() else (0, 120, 0)
                screen.blit(font.render(input_error, True, status_color), (10, WINDOW_HEIGHT - 16))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
