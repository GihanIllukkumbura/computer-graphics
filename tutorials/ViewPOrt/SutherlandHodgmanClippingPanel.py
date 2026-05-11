"""
Tutorial: Sutherland-Hodgman Polygon Clipping (Panel View)
=========================================================

Shows the original polygon on the left and a selected clipping stage on the right.

Controls:
    - 0: show final polygon
    - 1/2/3/4: show after Left/Right/Bottom/Top clipping
    - Left/Right: previous/next stage
    - U: toggle sample/user polygon
    - Click: add vertex in user mode (left panel)
    - T: type vertex coordinates
    - Space: switch X/Y while typing
    - Enter: add typed vertex
    - Backspace: delete a digit
    - D: delete last vertex
    - C: clear user polygon
    - K: toggle coordinates
    - H: toggle steps
    - G: toggle grid
    - R: reset to sample polygon
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
POLY_COLOR = (220, 60, 60)
CLIPPED_COLOR = (40, 150, 80)
TEXT_COLOR = (20, 20, 20)

SCALE = 7
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

# Polygon to be clipped
DEFAULT_POLYGON = [
    (10, 30),
    (30, 50),
    (60, 50),
    (70, 20),
    (40, 10),
]

STEPS = [
    "1) Clip against Left boundary.",
    "2) Clip against Right boundary.",
    "3) Clip against Bottom boundary.",
    "4) Clip against Top boundary.",
    "5) Output polygon is the final result.",
]


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


def intersect(p1, p2, boundary, vertical):
    x1, y1 = p1
    x2, y2 = p2
    if vertical:
        if abs(x2 - x1) < 1e-9:
            return boundary, y1
        y = y1 + (y2 - y1) * (boundary - x1) / (x2 - x1)
        return boundary, y
    if abs(y2 - y1) < 1e-9:
        return x1, boundary
    x = x1 + (x2 - x1) * (boundary - y1) / (y2 - y1)
    return x, boundary


def clip_left(poly):
    if not poly:
        return []
    result = []
    prev = poly[-1]
    for curr in poly:
        if curr[0] >= X_MIN:
            if prev[0] < X_MIN:
                result.append(intersect(prev, curr, X_MIN, True))
            result.append(curr)
        elif prev[0] >= X_MIN:
            result.append(intersect(prev, curr, X_MIN, True))
        prev = curr
    return result


def clip_right(poly):
    if not poly:
        return []
    result = []
    prev = poly[-1]
    for curr in poly:
        if curr[0] <= X_MAX:
            if prev[0] > X_MAX:
                result.append(intersect(prev, curr, X_MAX, True))
            result.append(curr)
        elif prev[0] <= X_MAX:
            result.append(intersect(prev, curr, X_MAX, True))
        prev = curr
    return result


def clip_bottom(poly):
    if not poly:
        return []
    result = []
    prev = poly[-1]
    for curr in poly:
        if curr[1] >= Y_MIN:
            if prev[1] < Y_MIN:
                result.append(intersect(prev, curr, Y_MIN, False))
            result.append(curr)
        elif prev[1] >= Y_MIN:
            result.append(intersect(prev, curr, Y_MIN, False))
        prev = curr
    return result


def clip_top(poly):
    if not poly:
        return []
    result = []
    prev = poly[-1]
    for curr in poly:
        if curr[1] <= Y_MAX:
            if prev[1] > Y_MAX:
                result.append(intersect(prev, curr, Y_MAX, False))
            result.append(curr)
        elif prev[1] <= Y_MAX:
            result.append(intersect(prev, curr, Y_MAX, False))
        prev = curr
    return result


def build_stages(poly):
    if len(poly) < 3:
        return [("Empty", [])]
    left = clip_left(poly)
    right = clip_right(left)
    bottom = clip_bottom(right)
    top = clip_top(bottom)
    return [
        ("Left", left),
        ("Right", right),
        ("Bottom", bottom),
        ("Top", top),
        ("Final", top),
    ]


def draw_polygon(surface, points, origin, color, width=2):
    if len(points) < 2:
        return
    screen_points = [world_to_screen(x, y, origin) for x, y in points]
    pygame.draw.polygon(surface, color, screen_points, width)
    for p in screen_points:
        pygame.draw.circle(surface, color, p, 4)


def draw_text_block(surface, lines, x, y, font, color=TEXT_COLOR, line_h=18):
    for i, text in enumerate(lines):
        label = font.render(text, True, color)
        surface.blit(label, (x, y + i * line_h))


def draw_text_block_bottom_right(surface, lines, font, color=TEXT_COLOR, line_h=18, margin=20):
    if not lines:
        return
    widths = [font.size(line)[0] for line in lines]
    block_width = max(widths)
    block_height = line_h * len(lines)
    x = surface.get_width() - margin - block_width
    y = surface.get_height() - margin - block_height
    draw_text_block(surface, lines, x, y, font, color=color, line_h=line_h)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Sutherland-Hodgman Polygon Clipping")
    font = pygame.font.SysFont("Consolas", 16)
    clock = pygame.time.Clock()

    show_grid = True
    show_coords = True
    show_steps = False

    use_custom = False
    custom_polygon = []

    input_mode = False
    active_field = "x"
    input_x = ""
    input_y = ""

    message = ""
    message_timer = 0

    stage_index = 4

    def set_message(text):
        nonlocal message, message_timer
        message = text
        message_timer = 180

    def reset_to_sample():
        nonlocal use_custom, custom_polygon, stage_index
        use_custom = False
        custom_polygon = []
        stage_index = 4

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if use_custom and not input_mode:
                    mx, my = event.pos
                    wx, wy = screen_to_world(mx, my, ORIGIN_LEFT)
                    custom_polygon.append((int(round(wx)), int(round(wy))))
            elif event.type == pygame.KEYDOWN:
                if input_mode:
                    if event.key == pygame.K_ESCAPE:
                        input_mode = False
                    elif event.key == pygame.K_SPACE:
                        active_field = "y" if active_field == "x" else "x"
                    elif event.key == pygame.K_RETURN:
                        if input_x and input_y:
                            try:
                                custom_polygon.append((int(input_x), int(input_y)))
                                use_custom = True
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
                        reset_to_sample()
                    elif event.key == pygame.K_u:
                        use_custom = not use_custom
                    elif event.key == pygame.K_c:
                        custom_polygon = []
                    elif event.key == pygame.K_d:
                        if custom_polygon:
                            custom_polygon.pop()
                    elif event.key == pygame.K_t:
                        input_mode = True
                        active_field = "x"
                        input_x = ""
                        input_y = ""
                    elif event.key == pygame.K_k:
                        show_coords = not show_coords
                    elif event.key == pygame.K_h:
                        show_steps = not show_steps
                    elif event.key == pygame.K_0:
                        stage_index = 4
                    elif event.key == pygame.K_1:
                        stage_index = 0
                    elif event.key == pygame.K_2:
                        stage_index = 1
                    elif event.key == pygame.K_3:
                        stage_index = 2
                    elif event.key == pygame.K_4:
                        stage_index = 3
                    elif event.key == pygame.K_RIGHT:
                        stage_index += 1
                    elif event.key == pygame.K_LEFT:
                        stage_index -= 1

        screen.fill(BG_COLOR)
        if show_grid:
            draw_grid(screen, ORIGIN_LEFT)
            draw_grid(screen, ORIGIN_RIGHT)

        draw_axes(screen, ORIGIN_LEFT)
        draw_axes(screen, ORIGIN_RIGHT)
        draw_rect(screen, ORIGIN_LEFT)
        draw_rect(screen, ORIGIN_RIGHT)

        polygon = custom_polygon if use_custom else DEFAULT_POLYGON
        stages = build_stages(polygon)
        if stage_index < 0:
            stage_index = len(stages) - 1
        if stage_index >= len(stages):
            stage_index = 0

        draw_polygon(screen, polygon, ORIGIN_LEFT, POLY_COLOR, width=2)

        stage_name, stage_poly = stages[stage_index]
        draw_polygon(screen, stage_poly, ORIGIN_RIGHT, CLIPPED_COLOR, width=3)

        title = font.render("Sutherland-Hodgman Polygon Clipping", True, TEXT_COLOR)
        screen.blit(title, (20, 15))

        left_label = font.render("Original", True, TEXT_COLOR)
        right_label = font.render(f"Stage: {stage_name}", True, TEXT_COLOR)
        screen.blit(left_label, (ORIGIN_LEFT[0], 40))
        screen.blit(right_label, (ORIGIN_RIGHT[0], 40))

        info = font.render(f"Vertices: {len(stage_poly)}", True, TEXT_COLOR)
        screen.blit(info, (ORIGIN_RIGHT[0], 65))

        help_text = font.render(
            "0-4: stage  |  Arrows: prev/next  |  U: user  |  T: type  |  D/C: del/clear  |  R: reset  |  G: grid",
            True,
            TEXT_COLOR,
        )
        screen.blit(help_text, (20, 90))

        hint_text = font.render("K: coords  |  H: steps  |  ESC: quit", True, TEXT_COLOR)
        screen.blit(hint_text, (20, 110))

        if input_mode:
            input_text = font.render(
                f"Typing  X={input_x or '_'}  Y={input_y or '_'}  (Space switch, Enter add)",
                True,
                TEXT_COLOR,
            )
            screen.blit(input_text, (20, 130))

        if show_coords:
            left_list = [
                f"P{i}: ({x}, {y})" for i, (x, y) in enumerate(polygon[:6], start=1)
            ]
            if len(polygon) > 6:
                left_list.append(f"... {len(polygon) - 6} more")
            draw_text_block(screen, left_list, 20, 145, font)

            right_list = [
                f"Q{i}: ({x:.1f}, {y:.1f})"
                for i, (x, y) in enumerate(stage_poly[:6], start=1)
            ]
            if len(stage_poly) > 6:
                right_list.append(f"... {len(stage_poly) - 6} more")
            draw_text_block(screen, right_list, 20, WINDOW_HEIGHT - 20 - (len(right_list) * 18), font)

        if show_steps:
            draw_text_block_bottom_right(screen, STEPS, font)

        if message_timer > 0:
            message_timer -= 1
            warn = font.render(message, True, (190, 60, 60))
            screen.blit(warn, (20, 275))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
