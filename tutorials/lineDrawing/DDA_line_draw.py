"""
Tutorial: DDA Line Drawing Algorithm
===================================

Demonstrates the DDA (Digital Differential Analyzer) line algorithm.
DDA uses incremental floating-point steps to generate line pixels between
two endpoints.

Controls:
    - Click two points to draw a DDA line
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


def plot_pixel(surface, x, y, color=LINE_COLOR, size=PIXEL_SIZE):
    """Plot one pixel at Cartesian coordinate (x, y)."""
    sx, sy = cartesian_to_screen(x, y)

    if size <= 1:
        if 0 <= sx < surface.get_width() and 0 <= sy < surface.get_height():
            surface.set_at((int(sx), int(sy)), color)
    else:
        pygame.draw.rect(surface, color, (int(sx) - size // 2, int(sy) - size // 2, size, size))


def draw_point_label(surface, font, x, y, color=TEXT_COLOR):
    """Show coordinate label near a point."""
    sx, sy = cartesian_to_screen(x, y)
    label = font.render(f"({x}, {y})", True, color)
    surface.blit(label, (int(sx) + 8, int(sy) - 18))


def dda_line(x0, y0, x1, y1):
    """
    DDA line algorithm.

    Steps:
    1. Compute dx, dy
    2. steps = max(|dx|, |dy|)
    3. x_inc = dx / steps, y_inc = dy / steps
    4. Plot round(x), round(y) for each step

    Returns a list of integer pixel coordinates.
    """
    dx = x1 - x0
    dy = y1 - y0

    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return [(x0, y0)]

    x_inc = dx / float(steps)
    y_inc = dy / float(steps)

    x = float(x0)
    y = float(y0)

    points = []
    for _ in range(steps + 1):
        points.append((round(x), round(y)))
        x += x_inc
        y += y_inc

    return points


def dda_line_trace(x0, y0, x1, y1):
    """
    DDA line algorithm with full step trace for teaching/debugging.

    Returns:
        trace: list of per-step dictionaries
        meta:  dictionary with dx, dy, steps, x_inc, y_inc
    """
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy))

    if steps == 0:
        trace = [{
            "step": 0,
            "x_float": float(x0),
            "y_float": float(y0),
            "pixel_x": x0,
            "pixel_y": y0,
        }]
        meta = {
            "dx": dx,
            "dy": dy,
            "steps": 0,
            "x_inc": 0.0,
            "y_inc": 0.0,
        }
        return trace, meta

    x_inc = dx / float(steps)
    y_inc = dy / float(steps)

    x = float(x0)
    y = float(y0)
    trace = []

    for step in range(steps + 1):
        trace.append({
            "step": step,
            "x_float": x,
            "y_float": y,
            "pixel_x": round(x),
            "pixel_y": round(y),
        })
        x += x_inc
        y += y_inc

    meta = {
        "dx": dx,
        "dy": dy,
        "steps": steps,
        "x_inc": x_inc,
        "y_inc": y_inc,
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
    pygame.display.set_caption("DDA Line Drawing Tutorial")
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
    example_pixels = dda_line(p1_example[0], p1_example[1], p2_example[0], p2_example[1])
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
                                debug_trace, debug_meta = dda_line_trace(p0[0], p0[1], p1[0], p1[1])
                                debug_points = (p0, p1)
                                debug_step = 0
                                input_error = "Debug trace loaded from typed points. Press SPACE to step."
                            else:
                                pixels = dda_line(p0[0], p0[1], p1[0], p1[1])
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
                        debug_trace, debug_meta = dda_line_trace(p0[0], p0[1], p1[0], p1[1])
                        debug_points = (p0, p1)
                        debug_step = 0
                    else:
                        pixels = dda_line(p0[0], p0[1], p1[0], p1[1])
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
                plot_pixel(screen, step_info["pixel_x"], step_info["pixel_y"], c, s)

            if debug_points is not None:
                p0, p1 = debug_points
                plot_pixel(screen, p0[0], p0[1], POINT_COLOR, 7)
                plot_pixel(screen, p1[0], p1[1], POINT_COLOR, 7)
                draw_point_label(screen, font, p0[0], p0[1], POINT_COLOR)
                draw_point_label(screen, font, p1[0], p1[1], POINT_COLOR)

        hud1 = font.render("DDA: Click 2 points | I=Input Mode | D=Debug | SPACE=Next | C=Clear | ESC=Quit", True, TEXT_COLOR)
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
                f"x_inc={debug_meta['x_inc']:.4f}  y_inc={debug_meta['y_inc']:.4f}"
            )
            debug_line_2 = (
                f"Step {current['step']}/{debug_meta['steps']}: "
                f"x={current['x_float']:.4f}, y={current['y_float']:.4f} "
                f"-> plot({current['pixel_x']}, {current['pixel_y']})"
            )
            debug_line_3 = "Formula each step: x = x + x_inc, y = y + y_inc"
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
