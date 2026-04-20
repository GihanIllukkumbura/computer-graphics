"""
Tutorial 10: Composing 2D Transformations About a Pivot
=======================================================

This tutorial demonstrates transformation composition with non-origin pivots.

Core idea:
    M_total = T(tx, ty) * T(px, py) * M_local * T(-px, -py)

Where:
    M_local = R(theta) * H(shx, shy) * S(sx, sy) * Ref(mode)

So every local transform is applied around the pivot by moving the
shape to origin first, applying transforms, then translating back.

Controls:
    - Mouse click: set pivot point
    - Arrow keys: translation tx, ty
    - Q/E: rotate angle -/+ degrees
    - Z/X: scale sx down/up
    - C/V: scale sy down/up
    - A/S: shear shx down/up
    - D/F: shear shy down/up
    - 0: reflection OFF (identity)
    - 1: reflect about local X-axis
    - 2: reflect about local Y-axis
    - 3: reflect about local origin
    - 4: reflect about local line y=x
    - 5: reflect about local line y=-x
    - Shift + controls: fine step
    - R: reset all parameters
    - ESC: quit
"""

import math
import pygame
import sys

# ============================================================
# Configuration
# ============================================================
WINDOW_WIDTH = 1320
WINDOW_HEIGHT = 820
BG_COLOR = (255, 255, 255)
GRID_COLOR = (238, 238, 238)
AXIS_COLOR = (180, 180, 180)
TEXT_COLOR = (20, 20, 20)
ORIGINAL_COLOR = (25, 80, 210)
TRANSFORM_COLOR = (210, 50, 60)
MAPPING_COLOR = (165, 165, 165)
PIVOT_COLOR = (0, 145, 70)
POINT_ORIGINAL_COLOR = (0, 110, 220)
POINT_TRANSFORM_COLOR = (220, 70, 80)

BASE_POLYGON = [(-130, -90), (80, -90), (150, 20), (-10, 130)]

REFLECTION_MATRICES = {
    "none": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
    "x": [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]],
    "y": [[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
    "origin": [[-1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]],
    "y=x": [[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]],
    "y=-x": [[0.0, -1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 1.0]],
}

REFLECTION_LABELS = {
    "none": "none",
    "x": "local X-axis",
    "y": "local Y-axis",
    "origin": "local origin",
    "y=x": "local y=x",
    "y=-x": "local y=-x",
}


def identity_matrix():
    """Return a 3x3 identity matrix."""
    return [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ]


def mat_mul(a, b):
    """Multiply two 3x3 matrices: result = a * b."""
    result = [[0.0, 0.0, 0.0] for _ in range(3)]
    for i in range(3):
        for j in range(3):
            result[i][j] = (
                a[i][0] * b[0][j]
                + a[i][1] * b[1][j]
                + a[i][2] * b[2][j]
            )
    return result


def translation_matrix(tx, ty):
    """Build homogeneous translation matrix."""
    return [
        [1.0, 0.0, tx],
        [0.0, 1.0, ty],
        [0.0, 0.0, 1.0],
    ]


def scaling_matrix(sx, sy):
    """Build homogeneous scaling matrix around origin."""
    return [
        [sx, 0.0, 0.0],
        [0.0, sy, 0.0],
        [0.0, 0.0, 1.0],
    ]


def rotation_matrix(angle_deg):
    """Build homogeneous rotation matrix around origin."""
    theta = math.radians(angle_deg)
    c = math.cos(theta)
    s = math.sin(theta)
    return [
        [c, -s, 0.0],
        [s, c, 0.0],
        [0.0, 0.0, 1.0],
    ]


def shear_matrix(shx, shy):
    """Build homogeneous matrix for combined x/y shear."""
    return [
        [1.0, shx, 0.0],
        [shy, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ]


def reflection_matrix(mode):
    """Get reflection matrix for current mode."""
    return REFLECTION_MATRICES[mode]


def apply_matrix(point, matrix):
    """Apply 3x3 homogeneous matrix to a 2D point."""
    x, y = point
    xp = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2]
    yp = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2]
    wp = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2]

    if abs(wp) < 1e-9:
        return x, y
    return xp / wp, yp / wp


def screen_to_cartesian(sx, sy):
    """Convert screen coordinates to Cartesian coordinates."""
    return sx - WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - sy


def cartesian_to_screen(cx, cy):
    """Convert Cartesian coordinates to screen coordinates."""
    return int(WINDOW_WIDTH // 2 + cx), int(WINDOW_HEIGHT // 2 - cy)


def draw_grid(surface, spacing=40):
    """Draw a light Cartesian grid."""
    w, h = surface.get_size()
    center_x, center_y = w // 2, h // 2

    for x in range(center_x % spacing, w, spacing):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, h), 1)
    for y in range(center_y % spacing, h, spacing):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (w, y), 1)


def draw_axes(surface):
    """Draw x and y axes crossing at origin."""
    w, h = surface.get_size()
    center_x, center_y = w // 2, h // 2
    pygame.draw.line(surface, AXIS_COLOR, (0, center_y), (w, center_y), 2)
    pygame.draw.line(surface, AXIS_COLOR, (center_x, 0), (center_x, h), 2)


def draw_polygon(surface, points, color, width=2):
    """Draw polygon edges from Cartesian point list."""
    if len(points) < 2:
        return
    screen_points = [cartesian_to_screen(x, y) for x, y in points]
    pygame.draw.polygon(surface, color, screen_points, width)


def draw_vertices(surface, font, points, prefix, color, point_color):
    """Draw vertex dots and coordinate labels."""
    for idx, (x, y) in enumerate(points, start=1):
        sx, sy = cartesian_to_screen(x, y)
        pygame.draw.circle(surface, point_color, (sx, sy), 5)
        label = font.render(
            f"{prefix}{idx}({int(round(x))}, {int(round(y))})",
            True,
            color,
        )
        surface.blit(label, (sx + 8, sy - 18))


def draw_mapping_lines(surface, original_points, transformed_points):
    """Draw correspondence lines between original and transformed vertices."""
    for (ox, oy), (tx, ty) in zip(original_points, transformed_points):
        pygame.draw.line(
            surface,
            MAPPING_COLOR,
            cartesian_to_screen(ox, oy),
            cartesian_to_screen(tx, ty),
            1,
        )


def draw_matrix_block(surface, font, title, matrix, top_left):
    """Render matrix values as HUD block."""
    x0, y0 = top_left
    surface.blit(font.render(title, True, TEXT_COLOR), (x0, y0))
    for row_index, row in enumerate(matrix):
        row_text = "| " + "  ".join(f"{value:>9.3f}" for value in row) + " |"
        surface.blit(font.render(row_text, True, TEXT_COLOR), (x0, y0 + 22 + row_index * 20))


def clamp_scale(value):
    """Keep scale factors stable and avoid exact zero collapse."""
    value = max(-3.0, min(3.0, value))
    if 0.0 < value < 0.05:
        return 0.05
    if -0.05 < value < 0.0:
        return -0.05
    return value


def compose_matrices(tx, ty, px, py, angle_deg, sx, sy, shx, shy, reflection_mode):
    """Build local and total composition matrices."""
    reflect_m = reflection_matrix(reflection_mode)
    scale_m = scaling_matrix(sx, sy)
    shear_m = shear_matrix(shx, shy)
    rotate_m = rotation_matrix(angle_deg)

    # Local order (right-to-left on points): Ref -> Scale -> Shear -> Rotate
    local_m = mat_mul(rotate_m, mat_mul(shear_m, mat_mul(scale_m, reflect_m)))

    to_origin = translation_matrix(-px, -py)
    from_origin = translation_matrix(px, py)
    world_translate = translation_matrix(tx, ty)

    around_pivot = mat_mul(from_origin, mat_mul(local_m, to_origin))
    total_m = mat_mul(world_translate, around_pivot)

    return local_m, total_m


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tutorial 10: Composing Transformations Around Pivot")
    font = pygame.font.SysFont("Consolas", 16)
    title_font = pygame.font.SysFont("Consolas", 20)
    clock = pygame.time.Clock()

    tx = 0.0
    ty = 0.0
    pivot = [0.0, 0.0]
    angle_deg = 0.0
    sx = 1.0
    sy = 1.0
    shx = 0.0
    shy = 0.0
    reflection_mode = "none"

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pivot[0], pivot[1] = screen_to_cartesian(*event.pos)
            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                fine = bool(mods & pygame.KMOD_SHIFT)

                trans_step = 2.0 if fine else 12.0
                angle_step = 1.0 if fine else 5.0
                scale_step = 0.02 if fine else 0.10
                shear_step = 0.02 if fine else 0.10

                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    tx = 0.0
                    ty = 0.0
                    pivot = [0.0, 0.0]
                    angle_deg = 0.0
                    sx = 1.0
                    sy = 1.0
                    shx = 0.0
                    shy = 0.0
                    reflection_mode = "none"

                elif event.key == pygame.K_LEFT:
                    tx -= trans_step
                elif event.key == pygame.K_RIGHT:
                    tx += trans_step
                elif event.key == pygame.K_UP:
                    ty += trans_step
                elif event.key == pygame.K_DOWN:
                    ty -= trans_step

                elif event.key == pygame.K_q:
                    angle_deg -= angle_step
                elif event.key == pygame.K_e:
                    angle_deg += angle_step

                elif event.key == pygame.K_z:
                    sx = clamp_scale(sx - scale_step)
                elif event.key == pygame.K_x:
                    sx = clamp_scale(sx + scale_step)
                elif event.key == pygame.K_c:
                    sy = clamp_scale(sy - scale_step)
                elif event.key == pygame.K_v:
                    sy = clamp_scale(sy + scale_step)

                elif event.key == pygame.K_a:
                    shx = max(-3.0, shx - shear_step)
                elif event.key == pygame.K_s:
                    shx = min(3.0, shx + shear_step)
                elif event.key == pygame.K_d:
                    shy = max(-3.0, shy - shear_step)
                elif event.key == pygame.K_f:
                    shy = min(3.0, shy + shear_step)

                elif event.key == pygame.K_0:
                    reflection_mode = "none"
                elif event.key == pygame.K_1:
                    reflection_mode = "x"
                elif event.key == pygame.K_2:
                    reflection_mode = "y"
                elif event.key == pygame.K_3:
                    reflection_mode = "origin"
                elif event.key == pygame.K_4:
                    reflection_mode = "y=x"
                elif event.key == pygame.K_5:
                    reflection_mode = "y=-x"

        local_m, total_m = compose_matrices(
            tx,
            ty,
            pivot[0],
            pivot[1],
            angle_deg,
            sx,
            sy,
            shx,
            shy,
            reflection_mode,
        )

        transformed_polygon = [apply_matrix(point, total_m) for point in BASE_POLYGON]

        screen.fill(BG_COLOR)
        draw_grid(screen)
        draw_axes(screen)

        draw_mapping_lines(screen, BASE_POLYGON, transformed_polygon)
        draw_polygon(screen, BASE_POLYGON, ORIGINAL_COLOR, 2)
        draw_polygon(screen, transformed_polygon, TRANSFORM_COLOR, 2)

        draw_vertices(screen, font, BASE_POLYGON, "V", ORIGINAL_COLOR, POINT_ORIGINAL_COLOR)
        draw_vertices(screen, font, transformed_polygon, "V'", TRANSFORM_COLOR, POINT_TRANSFORM_COLOR)

        pivot_screen = cartesian_to_screen(pivot[0], pivot[1])
        pygame.draw.circle(screen, PIVOT_COLOR, pivot_screen, 7)
        pygame.draw.circle(screen, BG_COLOR, pivot_screen, 3)
        pivot_label = font.render(
            f"Pivot ({int(round(pivot[0]))}, {int(round(pivot[1]))})",
            True,
            PIVOT_COLOR,
        )
        screen.blit(pivot_label, (pivot_screen[0] + 8, pivot_screen[1] - 24))

        title = title_font.render("Tutorial 10: Composing 2D Transformations", True, TEXT_COLOR)
        order_line = font.render(
            "Order on point: Ref -> Scale -> Shear -> Rotate, then pivot-wrap and world translate",
            True,
            TEXT_COLOR,
        )
        controls_line = font.render(
            "Arrows: tx/ty | Q/E: angle | Z/X: sx | C/V: sy | A/S: shx | D/F: shy | 0..5: reflection",
            True,
            TEXT_COLOR,
        )
        controls_line_2 = font.render(
            "Click: pivot | Shift: fine control | R: reset | ESC: quit",
            True,
            TEXT_COLOR,
        )

        params_line_1 = font.render(
            f"tx={tx:.2f}, ty={ty:.2f}, angle={angle_deg:.2f} deg, sx={sx:.2f}, sy={sy:.2f}",
            True,
            TEXT_COLOR,
        )
        params_line_2 = font.render(
            f"shx={shx:.2f}, shy={shy:.2f}, reflection={REFLECTION_LABELS[reflection_mode]}",
            True,
            TEXT_COLOR,
        )

        sample_original = BASE_POLYGON[0]
        sample_transformed = transformed_polygon[0]
        sample_line = font.render(
            (
                "Sample V1: "
                f"({sample_original[0]:.2f}, {sample_original[1]:.2f})"
                " -> "
                f"({sample_transformed[0]:.2f}, {sample_transformed[1]:.2f})"
            ),
            True,
            TEXT_COLOR,
        )

        legend_original = font.render("Blue: original shape", True, ORIGINAL_COLOR)
        legend_transformed = font.render("Red: composed result", True, TRANSFORM_COLOR)
        legend_mapping = font.render("Gray lines: original-to-result mapping", True, MAPPING_COLOR)

        screen.blit(title, (10, 10))
        screen.blit(order_line, (10, 40))
        screen.blit(controls_line, (10, 64))
        screen.blit(controls_line_2, (10, 88))
        screen.blit(params_line_1, (10, 112))
        screen.blit(params_line_2, (10, 136))
        screen.blit(sample_line, (10, 160))

        screen.blit(legend_original, (10, WINDOW_HEIGHT - 66))
        screen.blit(legend_transformed, (10, WINDOW_HEIGHT - 44))
        screen.blit(legend_mapping, (10, WINDOW_HEIGHT - 22))

        draw_matrix_block(screen, font, "Local Matrix M_local", local_m, (860, 24))
        draw_matrix_block(screen, font, "Total Matrix M_total", total_m, (860, 130))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
