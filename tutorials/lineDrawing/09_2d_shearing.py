"""
Tutorial 09: 2D Shearing (Matrix Visualization)
================================================

Interactive teaching GUI for 2D shearing.

X-shear:
    x' = x + shx*y
    y' = y
    Matrix:
        | 1  shx  0 |
        | 0   1   0 |
        | 0   0   1 |

Y-shear:
    x' = x
    y' = y + shy*x
    Matrix:
        | 1   0   0 |
        | shy 1   0 |
        | 0   0   1 |

Controls:
    - M: toggle between X-shear and Y-shear
    - Left/Right: decrease/increase shear factor
    - Shift + Left/Right: fine adjustment
    - R: reset mode and factor
    - ESC: quit
"""

import pygame
import sys

# ============================================================
# Configuration
# ============================================================
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 760
BG_COLOR = (255, 255, 255)
GRID_COLOR = (238, 238, 238)
AXIS_COLOR = (180, 180, 180)
TEXT_COLOR = (20, 20, 20)
ORIGINAL_COLOR = (25, 80, 210)
TRANSFORM_COLOR = (210, 50, 60)
MAPPING_COLOR = (165, 165, 165)
POINT_ORIGINAL_COLOR = (0, 110, 220)
POINT_TRANSFORM_COLOR = (220, 70, 80)

BASE_POLYGON = [(-130, -90), (80, -90), (150, 20), (-10, 130)]
MODE_NAMES = ["X-shear", "Y-shear"]


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


def apply_matrix(point, matrix):
    """Apply a 3x3 homogeneous matrix to a 2D point."""
    x, y = point
    xp = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2]
    yp = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2]
    wp = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2]

    if abs(wp) < 1e-9:
        return x, y
    return xp / wp, yp / wp


def draw_matrix_block(surface, font, title, matrix, top_left):
    """Render matrix values as a right-side HUD block."""
    x0, y0 = top_left
    surface.blit(font.render(title, True, TEXT_COLOR), (x0, y0))

    for row_index, row in enumerate(matrix):
        row_text = "| " + "  ".join(f"{value:>7.3f}" for value in row) + " |"
        surface.blit(font.render(row_text, True, TEXT_COLOR), (x0, y0 + 22 + row_index * 20))


def build_shear_matrix(mode_index, shear_factor):
    """Build matrix for current shearing mode."""
    if mode_index == 0:
        return [
            [1.0, shear_factor, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    return [
        [1.0, 0.0, 0.0],
        [shear_factor, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ]


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tutorial 09: 2D Shearing")
    font = pygame.font.SysFont("Consolas", 16)
    title_font = pygame.font.SysFont("Consolas", 20)
    clock = pygame.time.Clock()

    mode_index = 0
    shear_factor = 0.50

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                step = 0.02 if (mods & pygame.KMOD_SHIFT) else 0.1

                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_m:
                    mode_index = (mode_index + 1) % 2
                elif event.key == pygame.K_LEFT:
                    shear_factor = max(-3.0, shear_factor - step)
                elif event.key == pygame.K_RIGHT:
                    shear_factor = min(3.0, shear_factor + step)
                elif event.key == pygame.K_r:
                    mode_index = 0
                    shear_factor = 0.50

        shear_matrix = build_shear_matrix(mode_index, shear_factor)
        transformed_polygon = [
            apply_matrix(point, shear_matrix) for point in BASE_POLYGON
        ]

        screen.fill(BG_COLOR)
        draw_grid(screen)
        draw_axes(screen)

        draw_mapping_lines(screen, BASE_POLYGON, transformed_polygon)
        draw_polygon(screen, BASE_POLYGON, ORIGINAL_COLOR, 2)
        draw_polygon(screen, transformed_polygon, TRANSFORM_COLOR, 2)

        draw_vertices(screen, font, BASE_POLYGON, "V", ORIGINAL_COLOR, POINT_ORIGINAL_COLOR)
        draw_vertices(screen, font, transformed_polygon, "V'", TRANSFORM_COLOR, POINT_TRANSFORM_COLOR)

        mode_name = MODE_NAMES[mode_index]
        if mode_index == 0:
            equation = "x' = x + shx*y, y' = y"
        else:
            equation = "x' = x, y' = y + shy*x"

        title = title_font.render("2D Shearing", True, TEXT_COLOR)
        hud1 = font.render(
            "Controls: M = toggle mode | Left/Right = shear factor | Shift=Fine | R=Reset | ESC=Quit",
            True,
            TEXT_COLOR,
        )
        hud2 = font.render(f"Active mode: {mode_name}", True, TEXT_COLOR)
        hud3 = font.render(f"Shear factor: {shear_factor:.2f}", True, TEXT_COLOR)
        hud4 = font.render(f"Equation: {equation}", True, TEXT_COLOR)

        sample_original = BASE_POLYGON[0]
        sample_transformed = transformed_polygon[0]
        sample_line = font.render(
            (
                "Sample V1: "
                f"({sample_original[0]:.1f}, {sample_original[1]:.1f})"
                " -> "
                f"({sample_transformed[0]:.1f}, {sample_transformed[1]:.1f})"
            ),
            True,
            TEXT_COLOR,
        )

        legend_original = font.render("Blue: original shape", True, ORIGINAL_COLOR)
        legend_transformed = font.render("Red: sheared shape", True, TRANSFORM_COLOR)
        legend_mapping = font.render("Gray lines: vertex movement", True, MAPPING_COLOR)

        screen.blit(title, (10, 10))
        screen.blit(hud1, (10, 42))
        screen.blit(hud2, (10, 66))
        screen.blit(hud3, (10, 90))
        screen.blit(hud4, (10, 114))
        screen.blit(sample_line, (10, 138))
        screen.blit(legend_original, (10, WINDOW_HEIGHT - 66))
        screen.blit(legend_transformed, (10, WINDOW_HEIGHT - 44))
        screen.blit(legend_mapping, (10, WINDOW_HEIGHT - 22))

        draw_matrix_block(screen, font, "Shearing Matrix (3x3)", shear_matrix, (760, 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
