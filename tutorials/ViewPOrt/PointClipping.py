"""
Tutorial: Point Clipping (Interactive)
======================================

Checks whether a point lies inside a rectangular area of interest.

Controls:
    - Mouse click: place a point
    - T: type coordinates
    - Space: switch X/Y while typing
    - Enter: apply typed coordinates
    - Backspace: delete a digit
    - C: clear point
    - K: toggle coordinates
    - H: toggle steps
    - G: toggle grid
    - ESC: quit
"""

import pygame
import sys

# ============================================================
# Configuration
# ============================================================
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 650
BG_COLOR = (250, 250, 250)
GRID_COLOR = (235, 235, 235)
AXIS_COLOR = (170, 170, 170)
RECT_COLOR = (30, 30, 30)
POINT_INSIDE = (40, 150, 80)
POINT_OUTSIDE = (220, 60, 60)
TEXT_COLOR = (20, 20, 20)
WARN_COLOR = (190, 60, 60)

SCALE = 1
ORIGIN = (60, WINDOW_HEIGHT - 60)
GRID_MAX_X = 300
GRID_MAX_Y = 250
GRID_STEP = 25

# Area of interest
X_MIN = 50
Y_MIN = 50
X_MAX = 200
Y_MAX = 200

STEPS = [
    "1) Check if x is between x_min and x_max.",
    "2) Check if y is between y_min and y_max.",
    "3) Inside if both checks pass.",
]


def world_to_screen(x, y, origin=ORIGIN, scale=SCALE):
    return int(origin[0] + x * scale), int(origin[1] - y * scale)


def screen_to_world(sx, sy, origin=ORIGIN, scale=SCALE):
    return (sx - origin[0]) / scale, (origin[1] - sy) / scale


def draw_grid(surface, origin=ORIGIN, scale=SCALE):
    for x in range(0, GRID_MAX_X + 1, GRID_STEP):
        sx1, sy1 = world_to_screen(x, 0, origin, scale)
        sx2, sy2 = world_to_screen(x, GRID_MAX_Y, origin, scale)
        pygame.draw.line(surface, GRID_COLOR, (sx1, sy1), (sx2, sy2), 1)
    for y in range(0, GRID_MAX_Y + 1, GRID_STEP):
        sx1, sy1 = world_to_screen(0, y, origin, scale)
        sx2, sy2 = world_to_screen(GRID_MAX_X, y, origin, scale)
        pygame.draw.line(surface, GRID_COLOR, (sx1, sy1), (sx2, sy2), 1)


def draw_axes(surface, origin=ORIGIN, scale=SCALE):
    axis_len = 20 * scale
    ox, oy = origin
    pygame.draw.line(surface, AXIS_COLOR, (ox, oy), (ox + axis_len, oy), 2)
    pygame.draw.line(surface, AXIS_COLOR, (ox, oy), (ox, oy - axis_len), 2)


def draw_rect(surface, origin=ORIGIN, scale=SCALE, color=RECT_COLOR):
    top_left = world_to_screen(X_MIN, Y_MAX, origin, scale)
    width = int((X_MAX - X_MIN) * scale)
    height = int((Y_MAX - Y_MIN) * scale)
    pygame.draw.rect(surface, color, (top_left[0], top_left[1], width, height), 2)


def check_point_inside(x, y):
    return X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Point Clipping")
    font = pygame.font.SysFont("Consolas", 16)
    clock = pygame.time.Clock()

    point = None
    is_inside = False
    show_grid = True
    show_coords = True
    show_steps = False

    input_mode = False
    active_field = "x"
    input_x = ""
    input_y = ""
    message = ""
    message_timer = 0

    def set_message(text):
        nonlocal message, message_timer
        message = text
        message_timer = 180

    def set_point(x, y):
        nonlocal point, is_inside
        point = (int(round(x)), int(round(y)))
        is_inside = check_point_inside(point[0], point[1])

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not input_mode:
                mx, my = event.pos
                wx, wy = screen_to_world(mx, my)
                set_point(wx, wy)
            elif event.type == pygame.KEYDOWN:
                if input_mode:
                    if event.key == pygame.K_ESCAPE:
                        input_mode = False
                    elif event.key == pygame.K_SPACE:
                        active_field = "y" if active_field == "x" else "x"
                    elif event.key == pygame.K_RETURN:
                        if input_x and input_y:
                            try:
                                set_point(int(input_x), int(input_y))
                                input_mode = False
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
                    elif event.key == pygame.K_c:
                        point = None
                    elif event.key == pygame.K_g:
                        show_grid = not show_grid
                    elif event.key == pygame.K_t:
                        input_mode = True
                        active_field = "x"
                        input_x = ""
                        input_y = ""
                    elif event.key == pygame.K_k:
                        show_coords = not show_coords
                    elif event.key == pygame.K_h:
                        show_steps = not show_steps

        screen.fill(BG_COLOR)
        if show_grid:
            draw_grid(screen)
        draw_axes(screen)
        draw_rect(screen)

        if point:
            color = POINT_INSIDE if is_inside else POINT_OUTSIDE
            sx, sy = world_to_screen(point[0], point[1])
            pygame.draw.circle(screen, color, (sx, sy), 6)
            if show_coords:
                label = font.render(
                    f"Point: ({point[0]}, {point[1]}) - {'Inside' if is_inside else 'Outside'}",
                    True,
                    color,
                )
                screen.blit(label, (20, 40))

        title = font.render("Point Clipping", True, TEXT_COLOR)
        screen.blit(title, (20, 15))

        help_text = font.render(
            "Click: place point  |  T: type  |  C: clear  |  G: grid  |  K: coords  |  H: steps",
            True,
            TEXT_COLOR,
        )
        screen.blit(help_text, (20, 65))

        hint_text = font.render("ESC: quit", True, TEXT_COLOR)
        screen.blit(hint_text, (20, 85))

        if show_coords:
            region_text = font.render(
                f"Region: ({X_MIN}, {Y_MIN}) to ({X_MAX}, {Y_MAX})",
                True,
                TEXT_COLOR,
            )
            screen.blit(region_text, (20, 90))

        if input_mode:
            input_text = font.render(
                f"Typing  X={input_x or '_'}  Y={input_y or '_'}  (Space switch, Enter apply)",
                True,
                TEXT_COLOR,
            )
            screen.blit(input_text, (20, 115))

        if show_steps:
            for i, text in enumerate(STEPS):
                label = font.render(text, True, TEXT_COLOR)
                screen.blit(label, (20, 145 + i * 18))

        if message_timer > 0:
            message_timer -= 1
            warn = font.render(message, True, WARN_COLOR)
            screen.blit(warn, (20, 140))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
