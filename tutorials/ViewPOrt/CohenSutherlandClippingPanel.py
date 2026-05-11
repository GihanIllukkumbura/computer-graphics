"""
Tutorial: Cohen-Sutherland Line Clipping (Panel View)
=====================================================

Shows original lines on the left and the clipped result on the right.

Controls:
    - U: toggle sample/user lines
    - Click: add a line (two clicks) in user mode
    - T: type line coordinates
    - Space: switch field while typing
    - Enter: add typed line
    - Backspace: delete a digit
    - D: delete last user line
    - C: clear user lines
    - K: toggle coordinates
    - H: toggle steps
    - G: toggle grid
    - R: reset to sample lines
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
LINE_COLOR = (220, 60, 60)
CLIPPED_COLOR = (40, 150, 80)
TEXT_COLOR = (20, 20, 20)

SCALE = 10
ORIGIN_LEFT = (80, WINDOW_HEIGHT - 80)
ORIGIN_RIGHT = (WINDOW_WIDTH // 2 + 80, WINDOW_HEIGHT - 80)
GRID_MAX_X = 100
GRID_MAX_Y = 80
GRID_STEP = 10

# Clipping rectangle
X_MIN = 20
Y_MIN = 20
X_MAX = 50
Y_MAX = 40

# Sample lines (world coords)
DEFAULT_LINES = [
    (25, 25, 35, 35),
    (35, 45, 55, 20),
    (5, 25, 20, 5),
]

STEPS = [
    "1) Compute region codes for both endpoints.",
    "2) If both codes are 0, accept the line.",
    "3) If (code1 & code2) != 0, reject the line.",
    "4) Otherwise, intersect the outside endpoint with a boundary.",
    "5) Replace that endpoint and repeat.",
]

# Region codes
INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8


def world_to_screen(x, y, origin, scale=SCALE):
    return int(origin[0] + x * scale), int(origin[1] - y * scale)


def screen_to_world(sx, sy, origin, scale=SCALE):
    return (sx - origin[0]) / scale, (origin[1] - sy) / scale


def draw_grid(surface, origin, scale=SCALE):
    for x in range(0, GRID_MAX_X + 1, GRID_STEP):
        sx1, sy1 = world_to_screen(x, 0, origin, scale)
        sx2, sy2 = world_to_screen(x, GRID_MAX_Y, origin, scale)
        pygame.draw.line(surface, GRID_COLOR, (sx1, sy1), (sx2, sy2), 1)
    for y in range(0, GRID_MAX_Y + 1, GRID_STEP):
        sx1, sy1 = world_to_screen(0, y, origin, scale)
        sx2, sy2 = world_to_screen(GRID_MAX_X, y, origin, scale)
        pygame.draw.line(surface, GRID_COLOR, (sx1, sy1), (sx2, sy2), 1)


def draw_axes(surface, origin, scale=SCALE):
    axis_len = 15 * scale
    ox, oy = origin
    pygame.draw.line(surface, AXIS_COLOR, (ox, oy), (ox + axis_len, oy), 2)
    pygame.draw.line(surface, AXIS_COLOR, (ox, oy), (ox, oy - axis_len), 2)


def draw_rect(surface, origin, scale=SCALE, color=RECT_COLOR):
    top_left = world_to_screen(X_MIN, Y_MAX, origin, scale)
    width = int((X_MAX - X_MIN) * scale)
    height = int((Y_MAX - Y_MIN) * scale)
    pygame.draw.rect(surface, color, (top_left[0], top_left[1], width, height), 2)


def compute_code(x, y):
    code = INSIDE
    if x < X_MIN:
        code |= LEFT
    elif x > X_MAX:
        code |= RIGHT
    if y < Y_MIN:
        code |= BOTTOM
    elif y > Y_MAX:
        code |= TOP
    return code


def cohen_sutherland_clip(line):
    x1, y1, x2, y2 = line
    code1 = compute_code(x1, y1)
    code2 = compute_code(x2, y2)
    accept = False

    while True:
        if code1 == 0 and code2 == 0:
            accept = True
            break
        if (code1 & code2) != 0:
            break

        if code1 != 0:
            code_out = code1
        else:
            code_out = code2

        x, y = 0.0, 0.0
        if (code_out & TOP) != 0:
            x = x1 + (x2 - x1) * (Y_MAX - y1) / (y2 - y1)
            y = Y_MAX
        elif (code_out & BOTTOM) != 0:
            x = x1 + (x2 - x1) * (Y_MIN - y1) / (y2 - y1)
            y = Y_MIN
        elif (code_out & RIGHT) != 0:
            y = y1 + (y2 - y1) * (X_MAX - x1) / (x2 - x1)
            x = X_MAX
        elif (code_out & LEFT) != 0:
            y = y1 + (y2 - y1) * (X_MIN - x1) / (x2 - x1)
            x = X_MIN

        if code_out == code1:
            x1, y1 = x, y
            code1 = compute_code(x1, y1)
        else:
            x2, y2 = x, y
            code2 = compute_code(x2, y2)

    if accept:
        return x1, y1, x2, y2
    return None


def draw_line(surface, line, origin, color, width=2):
    x1, y1, x2, y2 = line
    p1 = world_to_screen(x1, y1, origin)
    p2 = world_to_screen(x2, y2, origin)
    pygame.draw.line(surface, color, p1, p2, width)


def draw_text_block(surface, lines, x, y, font, color=TEXT_COLOR, line_h=18):
    for i, text in enumerate(lines):
        label = font.render(text, True, color)
        surface.blit(label, (x, y + i * line_h))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Cohen-Sutherland Line Clipping (Panel)")
    font = pygame.font.SysFont("Consolas", 16)
    clock = pygame.time.Clock()

    show_grid = True
    show_coords = True
    show_steps = False

    use_custom = False
    user_lines = []
    pending_point = None

    input_mode = False
    active_field = 0
    fields = ["x1", "y1", "x2", "y2"]
    inputs = ["", "", "", ""]

    message = ""
    message_timer = 0

    def set_message(text):
        nonlocal message, message_timer
        message = text
        message_timer = 180

    def reset_to_sample():
        nonlocal use_custom, user_lines, pending_point
        use_custom = False
        user_lines = []
        pending_point = None

    def active_lines():
        return user_lines if use_custom else DEFAULT_LINES

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if use_custom and not input_mode:
                    mx, my = event.pos
                    wx, wy = screen_to_world(mx, my, ORIGIN_LEFT)
                    wx, wy = int(round(wx)), int(round(wy))
                    if pending_point is None:
                        pending_point = (wx, wy)
                    else:
                        user_lines.append((pending_point[0], pending_point[1], wx, wy))
                        pending_point = None
            elif event.type == pygame.KEYDOWN:
                if input_mode:
                    if event.key == pygame.K_ESCAPE:
                        input_mode = False
                    elif event.key == pygame.K_SPACE:
                        active_field = (active_field + 1) % len(fields)
                    elif event.key == pygame.K_RETURN:
                        if all(inputs):
                            try:
                                values = [float(v) for v in inputs]
                                user_lines.append((values[0], values[1], values[2], values[3]))
                                use_custom = True
                                inputs = ["", "", "", ""]
                                input_mode = False
                            except ValueError:
                                set_message("Invalid coordinates")
                        else:
                            set_message("Enter x1, y1, x2, y2")
                    elif event.key == pygame.K_BACKSPACE:
                        inputs[active_field] = inputs[active_field][:-1]
                    else:
                        ch = event.unicode
                        if ch.isdigit() or ch in "-.":
                            if ch == "." and "." in inputs[active_field]:
                                continue
                            if ch == "-" and inputs[active_field]:
                                continue
                            inputs[active_field] += ch
                else:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_g:
                        show_grid = not show_grid
                    elif event.key == pygame.K_r:
                        reset_to_sample()
                    elif event.key == pygame.K_u:
                        use_custom = not use_custom
                        pending_point = None
                    elif event.key == pygame.K_c:
                        user_lines = []
                        pending_point = None
                    elif event.key == pygame.K_d:
                        if user_lines:
                            user_lines.pop()
                    elif event.key == pygame.K_t:
                        input_mode = True
                        active_field = 0
                        inputs = ["", "", "", ""]
                    elif event.key == pygame.K_k:
                        show_coords = not show_coords
                    elif event.key == pygame.K_h:
                        show_steps = not show_steps

        screen.fill(BG_COLOR)
        if show_grid:
            draw_grid(screen, ORIGIN_LEFT)
            draw_grid(screen, ORIGIN_RIGHT)

        draw_axes(screen, ORIGIN_LEFT)
        draw_axes(screen, ORIGIN_RIGHT)
        draw_rect(screen, ORIGIN_LEFT)
        draw_rect(screen, ORIGIN_RIGHT)

        lines = active_lines()
        clipped_lines = [line for line in (cohen_sutherland_clip(l) for l in lines) if line]

        for line in lines:
            draw_line(screen, line, ORIGIN_LEFT, LINE_COLOR)
        for line in clipped_lines:
            draw_line(screen, line, ORIGIN_RIGHT, CLIPPED_COLOR, width=3)

        if pending_point:
            sp = world_to_screen(pending_point[0], pending_point[1], ORIGIN_LEFT)
            pygame.draw.circle(screen, LINE_COLOR, sp, 5)

        title = font.render("Cohen-Sutherland Line Clipping", True, TEXT_COLOR)
        screen.blit(title, (20, 15))

        left_label = font.render("Original", True, TEXT_COLOR)
        right_label = font.render("Clipped", True, TEXT_COLOR)
        screen.blit(left_label, (ORIGIN_LEFT[0], 40))
        screen.blit(right_label, (ORIGIN_RIGHT[0], 40))

        help_text = font.render(
            "U: user  |  T: type  |  K: coords  |  H: steps  |  G: grid  |  R: reset  |  ESC: quit",
            True,
            TEXT_COLOR,
        )
        screen.blit(help_text, (20, 65))

        if input_mode:
            input_text = "  ".join(
                f"{name}={value or '_'}" for name, value in zip(fields, inputs)
            )
            label = font.render(f"Typing: {input_text}", True, TEXT_COLOR)
            screen.blit(label, (20, 90))

        if show_coords and lines:
            coord_lines = []
            for i, line in enumerate(lines[:5], start=1):
                coord_lines.append(
                    f"L{i}: ({line[0]:.1f}, {line[1]:.1f}) -> ({line[2]:.1f}, {line[3]:.1f})"
                )
            if len(lines) > 5:
                coord_lines.append(f"... {len(lines) - 5} more")
            draw_text_block(screen, coord_lines, 20, 115, font)

        if show_steps:
            draw_text_block(screen, STEPS, 620, 40, font)

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
