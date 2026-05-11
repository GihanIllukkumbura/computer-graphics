"""
Tutorial: Window to Viewport Transformation
==========================================

Maps points from a window coordinate system to a viewport coordinate system.

Controls:
    - Mouse click: add a point (inside the window)
    - T: type point coordinates
    - Space: switch X/Y while typing
    - Enter: add typed point
    - Backspace: delete a digit
    - D: delete last point
    - C: clear points
    - K: toggle coordinates
    - H: toggle steps
    - R: reset to default points
    - G: toggle grid
    - ESC: quit
"""

import pygame
import sys

# ============================================================
# Configuration
# ============================================================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
BG_COLOR = (250, 250, 250)
GRID_COLOR = (235, 235, 235)
AXIS_COLOR = (170, 170, 170)
RECT_COLOR = (30, 30, 30)
POINT_COLOR = (40, 150, 80)
TEXT_COLOR = (20, 20, 20)

SCALE = 4
ORIGIN_LEFT = (80, WINDOW_HEIGHT - 90)
ORIGIN_RIGHT = (WINDOW_WIDTH // 2 + 80, WINDOW_HEIGHT - 90)
GRID_STEP = 10

# Window and viewport boundaries
X_WMIN, Y_WMIN = 0, 20
X_WMAX, Y_WMAX = 100, 100
X_VMIN, Y_VMIN = 10, 20
X_VMAX, Y_VMAX = 80, 80

DEFAULT_WINDOW_POINTS = [
    (30, 80),
    (40, 60),
    (50, 70),
    (60, 50),
    (70, 60),
]

STEPS = [
    "1) Compute sx and sy from window and viewport extents.",
    "2) For each point, shift to window origin.",
    "3) Scale by sx and sy.",
    "4) Shift into the viewport origin.",
]


def world_to_screen(x, y, origin, scale=SCALE):
    return int(origin[0] + x * scale), int(origin[1] - y * scale)


def screen_to_world(sx, sy, origin, scale=SCALE):
    return (sx - origin[0]) / scale, (origin[1] - sy) / scale


def draw_grid(surface, origin, max_x, max_y, scale=SCALE):
    for x in range(0, max_x + 1, GRID_STEP):
        sx1, sy1 = world_to_screen(x, 0, origin, scale)
        sx2, sy2 = world_to_screen(x, max_y, origin, scale)
        pygame.draw.line(surface, GRID_COLOR, (sx1, sy1), (sx2, sy2), 1)
    for y in range(0, max_y + 1, GRID_STEP):
        sx1, sy1 = world_to_screen(0, y, origin, scale)
        sx2, sy2 = world_to_screen(max_x, y, origin, scale)
        pygame.draw.line(surface, GRID_COLOR, (sx1, sy1), (sx2, sy2), 1)


def draw_axes(surface, origin, scale=SCALE):
    axis_len = 15 * scale
    ox, oy = origin
    pygame.draw.line(surface, AXIS_COLOR, (ox, oy), (ox + axis_len, oy), 2)
    pygame.draw.line(surface, AXIS_COLOR, (ox, oy), (ox, oy - axis_len), 2)


def draw_rect(surface, origin, x_min, y_min, x_max, y_max, scale=SCALE, color=RECT_COLOR):
    top_left = world_to_screen(x_min, y_max, origin, scale)
    width = int((x_max - x_min) * scale)
    height = int((y_max - y_min) * scale)
    pygame.draw.rect(surface, color, (top_left[0], top_left[1], width, height), 2)


def compute_viewport_points(points):
    sx = (X_VMAX - X_VMIN) / (X_WMAX - X_WMIN)
    sy = (Y_VMAX - Y_VMIN) / (Y_WMAX - Y_WMIN)
    mapped = []
    for xw, yw in points:
        xv = X_VMIN + (xw - X_WMIN) * sx
        yv = Y_VMIN + (yw - Y_WMIN) * sy
        mapped.append((xv, yv))
    return mapped, sx, sy


def draw_points(surface, points, origin, scale=SCALE, color=POINT_COLOR):
    for x, y in points:
        sx, sy = world_to_screen(x, y, origin, scale)
        pygame.draw.circle(surface, color, (sx, sy), 5)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Window to Viewport Transformation")
    font = pygame.font.SysFont("Consolas", 16)
    clock = pygame.time.Clock()

    show_grid = True
    show_coords = True
    show_steps = False
    window_points = list(DEFAULT_WINDOW_POINTS)

    input_mode = False
    active_field = "x"
    input_x = ""
    input_y = ""
    message = ""
    message_timer = 0

    def reset_points():
        nonlocal window_points
        window_points = list(DEFAULT_WINDOW_POINTS)

    def set_message(text):
        nonlocal message, message_timer
        message = text
        message_timer = 180

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not input_mode:
                mx, my = event.pos
                wx, wy = screen_to_world(mx, my, ORIGIN_LEFT)
                if X_WMIN <= wx <= X_WMAX and Y_WMIN <= wy <= Y_WMAX:
                    window_points.append((int(round(wx)), int(round(wy))))
            elif event.type == pygame.KEYDOWN:
                if input_mode:
                    if event.key == pygame.K_ESCAPE:
                        input_mode = False
                    elif event.key == pygame.K_SPACE:
                        active_field = "y" if active_field == "x" else "x"
                    elif event.key == pygame.K_RETURN:
                        if input_x and input_y:
                            try:
                                wx, wy = int(input_x), int(input_y)
                                if X_WMIN <= wx <= X_WMAX and Y_WMIN <= wy <= Y_WMAX:
                                    window_points.append((wx, wy))
                                else:
                                    set_message("Point outside window")
                                input_x = ""
                                input_y = ""
                            except ValueError:
                                set_message("Invalid coordinates")
                        else:
                            set_message("Enter both X and Y")
                    elif event.key == pygame.K_BACKSPACE:
                        if active_field == "x":
                            input_x = input_x[:-1]
                        else:
                            input_y = input_y[:-1]
                    else:
                        ch = event.unicode
                        if ch.isdigit() or (ch == "-" and (input_x if active_field == "x" else input_y) == ""):
                            if active_field == "x":
                                input_x += ch
                            else:
                                input_y += ch
                else:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_g:
                        show_grid = not show_grid
                    elif event.key == pygame.K_r:
                        reset_points()
                    elif event.key == pygame.K_c:
                        window_points = []
                    elif event.key == pygame.K_d:
                        if window_points:
                            window_points.pop()
                    elif event.key == pygame.K_t:
                        input_mode = True
                        active_field = "x"
                        input_x = ""
                        input_y = ""
                    elif event.key == pygame.K_k:
                        show_coords = not show_coords
                    elif event.key == pygame.K_h:
                        show_steps = not show_steps

        viewport_points, sx, sy = compute_viewport_points(window_points)

        screen.fill(BG_COLOR)
        if show_grid:
            draw_grid(screen, ORIGIN_LEFT, X_WMAX, Y_WMAX)
            draw_grid(screen, ORIGIN_RIGHT, X_VMAX, Y_VMAX)

        draw_axes(screen, ORIGIN_LEFT)
        draw_axes(screen, ORIGIN_RIGHT)
        draw_rect(screen, ORIGIN_LEFT, X_WMIN, Y_WMIN, X_WMAX, Y_WMAX)
        draw_rect(screen, ORIGIN_RIGHT, X_VMIN, Y_VMIN, X_VMAX, Y_VMAX)

        draw_points(screen, window_points, ORIGIN_LEFT)
        draw_points(screen, viewport_points, ORIGIN_RIGHT)

        title = font.render("Window to Viewport Transformation", True, TEXT_COLOR)
        screen.blit(title, (20, 15))

        left_label = font.render("Window", True, TEXT_COLOR)
        right_label = font.render("Viewport", True, TEXT_COLOR)
        screen.blit(left_label, (ORIGIN_LEFT[0], 40))
        screen.blit(right_label, (ORIGIN_RIGHT[0], 40))

        help_text = font.render(
            "Click: add  |  T: type  |  D: delete  |  C: clear  |  R: reset  |  G: grid  |  K/H: coords/steps",
            True,
            TEXT_COLOR,
        )
        screen.blit(help_text, (20, 65))

        hint_text = font.render("ESC: quit", True, TEXT_COLOR)
        screen.blit(hint_text, (20, 85))

        info_y = 95
        scale_text = font.render(f"sx = {sx:.2f}, sy = {sy:.2f}", True, TEXT_COLOR)
        screen.blit(scale_text, (20, info_y))
        info_y += 22

        if show_coords:
            for i, (w, v) in enumerate(zip(window_points, viewport_points), start=1):
                if info_y > WINDOW_HEIGHT - 30:
                    break
                line = font.render(
                    f"P{i}: W({w[0]}, {w[1]}) -> V({int(round(v[0]))}, {int(round(v[1]))})",
                    True,
                    TEXT_COLOR,
                )
                screen.blit(line, (20, info_y))
                info_y += 20

            if len(window_points) > 12:
                more = font.render(f"... {len(window_points) - 12} more points", True, TEXT_COLOR)
                screen.blit(more, (20, WINDOW_HEIGHT - 30))

        if input_mode:
            input_text = font.render(
                f"Typing  X={input_x or '_'}  Y={input_y or '_'}  (Space switch, Enter add)",
                True,
                TEXT_COLOR,
            )
            screen.blit(input_text, (20, 115))

        if show_steps:
            for i, text in enumerate(STEPS):
                label = font.render(text, True, TEXT_COLOR)
                screen.blit(label, (620, 95 + i * 18))

        if message_timer > 0:
            message_timer -= 1
            warn = font.render(message, True, (190, 60, 60))
            screen.blit(warn, (20, 140))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
