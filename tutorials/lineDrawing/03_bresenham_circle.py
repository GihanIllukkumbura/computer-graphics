"""
Tutorial: Bresenham Circle Drawing Algorithm
===========================================

Demonstrates Bresenham's circle algorithm (midpoint circle method).
The algorithm uses integer arithmetic and 8-way symmetry to draw a
circle on a Cartesian plane.

Controls:
    - Click center, then click radius point to draw a circle
    - I = Toggle typed-input mode
    - Enter = Draw using typed input
    - D = Toggle debug mode
    - SPACE = Next step (in debug mode)
    - C = Clear all drawn circles
    - ESC = Quit
"""

import math
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
CIRCLE_COLOR = (0, 90, 200)
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


def plot_pixel(surface, x, y, color=CIRCLE_COLOR, size=PIXEL_SIZE):
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


def circle_symmetric_points(xc, yc, x, y):
    """Return the 8 symmetric circle points around center (xc, yc)."""
    points = [
        (xc + x, yc + y),
        (xc + x, yc - y),
        (xc - x, yc + y),
        (xc - x, yc - y),
        (xc + y, yc + x),
        (xc + y, yc - x),
        (xc - y, yc + x),
        (xc - y, yc - x),
    ]

    # Remove duplicate points for x==0, y==0, or x==y cases.
    unique = []
    seen = set()
    for point in points:
        if point not in seen:
            seen.add(point)
            unique.append(point)
    return unique


def bresenham_circle(xc, yc, r):
    """
    Bresenham circle algorithm.

    Returns a list of integer pixel coordinates.
    """
    if r == 0:
        return [(xc, yc)]

    points = []
    x = 0
    y = r
    p = 3 - (2 * r)

    points.extend(circle_symmetric_points(xc, yc, x, y))

    while x <= y:
        if p < 0:
            p = p + (4 * x) + 6
        else:
            p = p + (4 * (x - y)) + 10
            y -= 1

        x += 1
        points.extend(circle_symmetric_points(xc, yc, x, y))

    return points


def bresenham_circle_trace(xc, yc, r):
    """
    Bresenham circle algorithm with full step trace for teaching/debugging.

    Returns:
        trace: list of per-step dictionaries
        meta:  dictionary with r, initial_p, total_steps
    """
    if r == 0:
        trace = [{
            "step": 0,
            "x": 0,
            "y": 0,
            "p": 0,
            "decision": "single point",
        }]
        meta = {
            "r": 0,
            "initial_p": 0,
            "total_steps": 0,
        }
        return trace, meta

    x = 0
    y = r
    p = 3 - (2 * r)

    trace = [{
        "step": 0,
        "x": x,
        "y": y,
        "p": p,
        "decision": "start",
    }]

    step = 1
    while x <= y:
        old_p = p

        if p < 0:
            p = p + (4 * x) + 6
            decision = f"p={old_p}<0 -> y stays"
        else:
            p = p + (4 * (x - y)) + 10
            y -= 1
            decision = f"p={old_p}>=0 -> y decreases"

        x += 1
        trace.append({
            "step": step,
            "x": x,
            "y": y,
            "p": p,
            "decision": decision,
        })
        step += 1

    meta = {
        "r": r,
        "initial_p": 3 - (2 * r),
        "total_steps": len(trace) - 1,
    }
    return trace, meta


def parse_typed_circle(input_text):
    """
    Parse typed input and return center + radius.

    Supported formats:
      - xc yc r
      - xc,yc r
      - xc yc xr yr     (xr, yr is a radius point)
      - xc,yc xr,yr
    """
    cleaned = input_text.replace(",", " ").strip()
    parts = [p for p in cleaned.split() if p]

    if len(parts) == 3:
        xc, yc, r = map(int, parts)
    elif len(parts) == 4:
        xc, yc, xr, yr = map(int, parts)
        r = int(round(math.hypot(xr - xc, yr - yc)))
    else:
        raise ValueError("Use: xc yc r OR xc,yc r OR xc yc xr yr")

    if r <= 0:
        raise ValueError("Radius must be positive")

    return (xc, yc), r


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Bresenham Circle Drawing Tutorial")
    font = pygame.font.SysFont("Consolas", 15)
    clock = pygame.time.Clock()

    click_points = []
    drawn_circles = []
    debug_mode = False
    debug_trace = []
    debug_meta = None
    debug_circle = None
    debug_step = 0
    input_mode = False
    input_buffer = ""
    input_error = ""

    # Example circle visible at startup.
    example_center = (0, 0)
    example_r = 150
    example_pixels = bresenham_circle(example_center[0], example_center[1], example_r)
    drawn_circles.append(("Example", example_pixels, EXAMPLE_COLOR, example_center, example_r))

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
                    drawn_circles.clear()
                    debug_trace.clear()
                    debug_meta = None
                    debug_circle = None
                    debug_step = 0
                    input_buffer = ""
                    input_error = "Cleared all circles and inputs."
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
                        debug_circle = None
                        debug_step = 0
                elif input_mode:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        try:
                            center, radius = parse_typed_circle(input_buffer)
                            if debug_mode:
                                debug_trace, debug_meta = bresenham_circle_trace(center[0], center[1], radius)
                                debug_circle = (center, radius)
                                debug_step = 0
                                input_error = "Debug trace loaded from typed input. Press SPACE to step."
                            else:
                                pixels = bresenham_circle(center[0], center[1], radius)
                                label = f"Center({center[0]},{center[1]}) r={radius}"
                                drawn_circles.append((label, pixels, CIRCLE_COLOR, center, radius))
                                input_error = "Circle created from typed input."
                        except ValueError as exc:
                            input_error = str(exc)
                    elif event.key == pygame.K_BACKSPACE:
                        input_buffer = input_buffer[:-1]
                    else:
                        if event.unicode and event.unicode in "0123456789-, ":
                            input_buffer += event.unicode
                elif event.key == pygame.K_SPACE and debug_mode and debug_trace:
                    debug_step = min(debug_step + 1, len(debug_trace) - 1)

            elif event.type == pygame.MOUSEBUTTONDOWN and not input_mode:
                mx, my = event.pos
                click_points.append(screen_to_cartesian(mx, my))

                if len(click_points) == 2:
                    center = click_points[0]
                    radius_point = click_points[1]
                    radius = int(round(math.hypot(radius_point[0] - center[0], radius_point[1] - center[1])))

                    if radius <= 0:
                        input_error = "Radius must be positive. Choose a second point farther from center."
                    elif debug_mode:
                        debug_trace, debug_meta = bresenham_circle_trace(center[0], center[1], radius)
                        debug_circle = (center, radius)
                        debug_step = 0
                    else:
                        pixels = bresenham_circle(center[0], center[1], radius)
                        label = f"Center({center[0]},{center[1]}) r={radius}"
                        drawn_circles.append((label, pixels, CIRCLE_COLOR, center, radius))

                    click_points.clear()

        screen.fill(BG_COLOR)
        draw_grid(screen)
        draw_axes(screen)

        for _, pixels, color, center, _ in drawn_circles:
            for px, py in pixels:
                plot_pixel(screen, px, py, color)

            plot_pixel(screen, center[0], center[1], POINT_COLOR, 7)
            draw_point_label(screen, font, center[0], center[1], POINT_COLOR)

        if debug_mode and debug_trace and debug_circle is not None:
            center, _ = debug_circle

            for i in range(debug_step + 1):
                step_info = debug_trace[i]
                points = circle_symmetric_points(center[0], center[1], step_info["x"], step_info["y"])

                draw_color = HIGHLIGHT_COLOR if i == debug_step else CIRCLE_COLOR
                draw_size = 8 if i == debug_step else max(PIXEL_SIZE, 4)
                for px, py in points:
                    plot_pixel(screen, px, py, draw_color, draw_size)

            plot_pixel(screen, center[0], center[1], POINT_COLOR, 7)
            draw_point_label(screen, font, center[0], center[1], POINT_COLOR)

        if len(click_points) == 1:
            center = click_points[0]
            plot_pixel(screen, center[0], center[1], POINT_COLOR, 7)
            draw_point_label(screen, font, center[0], center[1], POINT_COLOR)

            mx, my = pygame.mouse.get_pos()
            current = screen_to_cartesian(mx, my)
            preview_r = int(round(math.hypot(current[0] - center[0], current[1] - center[1])))
            if preview_r > 0:
                preview_pixels = bresenham_circle(center[0], center[1], preview_r)
                for px, py in preview_pixels:
                    plot_pixel(screen, px, py, (190, 190, 190), 1)

        hud1 = font.render(
            "Bresenham Circle: Click center + radius point | I=Input Mode | D=Debug | SPACE=Next | C=Clear | ESC=Quit",
            True,
            TEXT_COLOR,
        )
        hud2 = font.render(f"Stored circles: {len(drawn_circles)}", True, TEXT_COLOR)
        screen.blit(hud1, (10, 10))
        screen.blit(hud2, (10, 32))

        mode_text = "Mode: DEBUG" if debug_mode else "Mode: NORMAL"
        input_text = "Input: TYPED" if input_mode else "Input: MOUSE"
        hud3 = font.render(f"{mode_text} | {input_text}", True, DEBUG_TEXT_COLOR)
        screen.blit(hud3, (10, 54))

        if debug_mode and debug_trace and debug_meta is not None:
            current = debug_trace[debug_step]
            debug_line_1 = (
                f"r={debug_meta['r']}  initial_p={debug_meta['initial_p']}  total_steps={debug_meta['total_steps']}"
            )
            debug_line_2 = (
                f"Step {current['step']}/{debug_meta['total_steps']}: "
                f"x={current['x']}, y={current['y']}  p={current['p']}"
            )
            debug_line_3 = f"Decision: {current['decision']}"
            debug_line_4 = "Formula: p=3-2*r; if p<0 -> p+=4*x+6 else -> p+=4*(x-y)+10, y=y-1"

            screen.blit(font.render(debug_line_1, True, DEBUG_TEXT_COLOR), (10, 76))
            screen.blit(font.render(debug_line_2, True, DEBUG_TEXT_COLOR), (10, 98))
            screen.blit(font.render(debug_line_3, True, DEBUG_TEXT_COLOR), (10, 120))
            screen.blit(font.render(debug_line_4, True, DEBUG_TEXT_COLOR), (10, 142))

        if len(click_points) == 1:
            p = click_points[0]
            msg = font.render(f"Center selected: ({p[0]}, {p[1]}). Click radius point.", True, TEXT_COLOR)
            screen.blit(msg, (10, 164 if debug_mode and debug_trace else 76))

        if input_mode:
            input_line = f"Typed values: {input_buffer}"
            input_hint = "Enter: xc yc r  OR  xc,yc r  OR  xc yc xr yr | Press Enter to draw"
            screen.blit(font.render(input_hint, True, DEBUG_TEXT_COLOR), (10, WINDOW_HEIGHT - 58))
            screen.blit(font.render(input_line, True, DEBUG_TEXT_COLOR), (10, WINDOW_HEIGHT - 36))

            if input_error:
                status_color = (160, 0, 0) if "format" in input_error.lower() or "positive" in input_error.lower() else (0, 120, 0)
                screen.blit(font.render(input_error, True, status_color), (10, WINDOW_HEIGHT - 16))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
