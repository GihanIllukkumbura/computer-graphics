"""
Tutorial: Liang-Barsky Line Clipping (Interactive)
==================================================

Uses the parametric form of a line to clip against a rectangular window.

Controls:
    - Left/Right: previous/next line
    - Space: toggle clipped segment
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
    - R: reset to sample lines
    - G: toggle grid
    - ESC: quit
"""

import pygame
import sys

# ============================================================
# Configuration
# ============================================================
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 650
BG_COLOR = (250, 250, 250)
GRID_COLOR = (235, 235, 235)
AXIS_COLOR = (170, 170, 170)
RECT_COLOR = (30, 30, 30)
LINE_COLOR = (220, 60, 60)
CLIPPED_COLOR = (40, 150, 80)
TEXT_COLOR = (20, 20, 20)

SCALE = 10
ORIGIN = (80, WINDOW_HEIGHT - 80)
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
    "1) Write the line in parametric form x(u), y(u).",
    "2) Build p and q for the 4 boundaries.",
    "3) Update u1 (enter) and u2 (leave).",
    "4) If u1 > u2, reject the line.",
    "5) Otherwise compute clipped endpoints.",
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
    axis_len = 15 * scale
    ox, oy = origin
    pygame.draw.line(surface, AXIS_COLOR, (ox, oy), (ox + axis_len, oy), 2)
    pygame.draw.line(surface, AXIS_COLOR, (ox, oy), (ox, oy - axis_len), 2)


def draw_rect(surface, origin=ORIGIN, scale=SCALE, color=RECT_COLOR):
    top_left = world_to_screen(X_MIN, Y_MAX, origin, scale)
    width = int((X_MAX - X_MIN) * scale)
    height = int((Y_MAX - Y_MIN) * scale)
    pygame.draw.rect(surface, color, (top_left[0], top_left[1], width, height), 2)


def liang_barsky_clip(line):
    x1, y1, x2, y2 = line
    p1 = -(x2 - x1)
    p2 = -p1
    p3 = -(y2 - y1)
    p4 = -p3

    q1 = x1 - X_MIN
    q2 = X_MAX - x1
    q3 = y1 - Y_MIN
    q4 = Y_MAX - y1

    p = [p1, p2, p3, p4]
    q = [q1, q2, q3, q4]

    u1, u2 = 0.0, 1.0
    for i in range(4):
        if p[i] < 0:
            u1 = max(u1, q[i] / p[i])
        elif p[i] > 0:
            u2 = min(u2, q[i] / p[i])
        elif q[i] < 0:
            return None

    if u1 > u2:
        return None

    nx1 = x1 + u1 * (x2 - x1)
    ny1 = y1 + u1 * (y2 - y1)
    nx2 = x1 + u2 * (x2 - x1)
    ny2 = y1 + u2 * (y2 - y1)
    return nx1, ny1, nx2, ny2


def draw_line(surface, line, origin=ORIGIN, scale=SCALE, color=LINE_COLOR, width=2):
    x1, y1, x2, y2 = line
    p1 = world_to_screen(x1, y1, origin, scale)
    p2 = world_to_screen(x2, y2, origin, scale)
    pygame.draw.line(surface, color, p1, p2, width)
    pygame.draw.circle(surface, color, p1, 4)
    pygame.draw.circle(surface, color, p2, 4)


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
    pygame.display.set_caption("Liang-Barsky Line Clipping")
    font = pygame.font.SysFont("Consolas", 16)
    clock = pygame.time.Clock()

    index = 0
    show_clip = False
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
        nonlocal use_custom, user_lines, index, pending_point, show_clip
        use_custom = False
        user_lines = []
        index = 0
        pending_point = None
        show_clip = False

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
                    wx, wy = screen_to_world(mx, my)
                    wx, wy = int(round(wx)), int(round(wy))
                    if pending_point is None:
                        pending_point = (wx, wy)
                    else:
                        user_lines.append((pending_point[0], pending_point[1], wx, wy))
                        pending_point = None
                        index = len(user_lines) - 1
                        show_clip = False
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
                                index = len(user_lines) - 1
                                show_clip = False
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
                    elif event.key == pygame.K_LEFT:
                        lines = active_lines()
                        if lines:
                            index = (index - 1) % len(lines)
                            show_clip = False
                    elif event.key == pygame.K_RIGHT:
                        lines = active_lines()
                        if lines:
                            index = (index + 1) % len(lines)
                            show_clip = False
                    elif event.key == pygame.K_SPACE:
                        show_clip = not show_clip
                    elif event.key == pygame.K_r:
                        reset_to_sample()
                    elif event.key == pygame.K_g:
                        show_grid = not show_grid
                    elif event.key == pygame.K_u:
                        use_custom = not use_custom
                        pending_point = None
                        lines = active_lines()
                        index = 0 if lines else 0
                        show_clip = False
                    elif event.key == pygame.K_c:
                        user_lines = []
                        index = 0
                        pending_point = None
                        show_clip = False
                    elif event.key == pygame.K_d:
                        if user_lines:
                            user_lines.pop()
                            index = max(0, index - 1)
                            show_clip = False
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
            draw_grid(screen)
        draw_axes(screen)
        draw_rect(screen)

        lines = active_lines()
        line = None
        clipped = None
        status = "No line"
        if lines:
            if index >= len(lines):
                index = 0
            line = lines[index]
            clipped = liang_barsky_clip(line)
            status = "Accepted" if clipped else "Rejected"

        if line:
            draw_line(screen, line, color=LINE_COLOR)
        if show_clip and clipped:
            draw_line(screen, clipped, color=CLIPPED_COLOR, width=3)

        if pending_point:
            sp = world_to_screen(pending_point[0], pending_point[1])
            pygame.draw.circle(screen, LINE_COLOR, sp, 5)
            mx, my = pygame.mouse.get_pos()
            pygame.draw.line(screen, AXIS_COLOR, sp, (mx, my), 1)

        title = font.render("Liang-Barsky Line Clipping", True, TEXT_COLOR)
        screen.blit(title, (20, 15))

        mode = "User" if use_custom else "Sample"
        count = len(lines)
        info = font.render(
            f"Mode: {mode}  |  Line {index + 1 if count else 0}/{count}  |  Status: {status}",
            True,
            TEXT_COLOR,
        )
        screen.blit(info, (20, 40))

        help_text = font.render(
            "Arrows: prev/next  |  Space: clip  |  U: user  |  T: type  |  D/C: del/clear  |  R: reset  |  G: grid",
            True,
            TEXT_COLOR,
        )
        screen.blit(help_text, (20, 65))

        hint_text = font.render(
            "K: coords  |  H: steps  |  ESC: quit",
            True,
            TEXT_COLOR,
        )
        screen.blit(hint_text, (20, 85))

        if input_mode:
            input_text = "  ".join(
                f"{name}={value or '_'}" for name, value in zip(fields, inputs)
            )
            label = font.render(f"Typing: {input_text}", True, TEXT_COLOR)
            screen.blit(label, (20, 110))

        overlay_lines = []
        if show_steps:
            overlay_lines.append("Steps:")
            overlay_lines.extend(STEPS)
        if show_coords:
            if overlay_lines:
                overlay_lines.append("")
            overlay_lines.append("Window rectangle:")
            overlay_lines.append(f"A=({X_MIN:.1f}, {Y_MIN:.1f})")
            overlay_lines.append(f"B=({X_MIN:.1f}, {Y_MAX:.1f})")
            overlay_lines.append(f"C=({X_MAX:.1f}, {Y_MAX:.1f})")
            overlay_lines.append(f"D=({X_MAX:.1f}, {Y_MIN:.1f})")
            if clipped:
                overlay_lines.append("Viewport coords:")
                overlay_lines.append(
                    f"P1=({clipped[0]:.1f}, {clipped[1]:.1f})"
                )
                overlay_lines.append(
                    f"P2=({clipped[2]:.1f}, {clipped[3]:.1f})"
                )
            else:
                overlay_lines.append("Viewport coords: none")

        draw_text_block_bottom_right(screen, overlay_lines, font)

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
