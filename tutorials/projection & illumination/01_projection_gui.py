"""
Interactive Projection GUI
==========================

Shows two common projection types side by side:
  1. Orthographic / parallel projection
  2. Perspective projection

Controls:
  - Left mouse drag: rotate the cube
  - Mouse wheel: zoom
  - Arrow keys: rotate
  - W / S: move camera distance for perspective
  - R: reset
  - Esc / Q: quit
"""

import math
import pygame


WIDTH, HEIGHT = 1200, 720
BG_COLOR = (245, 247, 250)
PANEL_COLOR = (255, 255, 255)
GRID_COLOR = (226, 232, 240)
TEXT_COLOR = (20, 27, 38)
MUTED_TEXT = (94, 103, 115)
EDGE_COLOR = (36, 76, 140)
ORTHO_COLOR = (28, 119, 107)
PERSPECTIVE_COLOR = (184, 78, 36)
AXIS_X = (210, 64, 64)
AXIS_Y = (60, 148, 78)
AXIS_Z = (72, 95, 180)


CUBE_VERTICES = [
    (-1, -1, -1),
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, 1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, 1, 1),
]

CUBE_EDGES = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),
]


def rotate_point(point, angle_x, angle_y, angle_z):
    x, y, z = point

    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x

    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
    x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y

    cos_z, sin_z = math.cos(angle_z), math.sin(angle_z)
    x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z

    return x, y, z


def project_orthographic(point, center, scale):
    x, y, _ = point
    return int(center[0] + x * scale), int(center[1] - y * scale)


def project_perspective(point, center, scale, camera_distance):
    x, y, z = point
    denominator = camera_distance - z
    factor = camera_distance / max(0.1, denominator)
    return int(center[0] + x * scale * factor), int(center[1] - y * scale * factor)


def draw_text(surface, font, text, x, y, color=TEXT_COLOR):
    label = font.render(text, True, color)
    surface.blit(label, (x, y))
    return y + font.get_linesize()


def draw_panel(surface, rect, title, subtitle, font, title_font):
    pygame.draw.rect(surface, PANEL_COLOR, rect, border_radius=8)
    pygame.draw.rect(surface, (210, 218, 229), rect, 1, border_radius=8)
    draw_text(surface, title_font, title, rect.x + 18, rect.y + 16)
    draw_text(surface, font, subtitle, rect.x + 18, rect.y + 46, MUTED_TEXT)


def draw_grid(surface, center, size, step=50):
    left = center[0] - size
    right = center[0] + size
    top = center[1] - size
    bottom = center[1] + size

    for x in range(left, right + 1, step):
        pygame.draw.line(surface, GRID_COLOR, (x, top), (x, bottom), 1)
    for y in range(top, bottom + 1, step):
        pygame.draw.line(surface, GRID_COLOR, (left, y), (right, y), 1)


def draw_axes(surface, center, projected_axes, font):
    axis_data = [
        ("X", projected_axes[0], AXIS_X),
        ("Y", projected_axes[1], AXIS_Y),
        ("Z", projected_axes[2], AXIS_Z),
    ]
    for label, end, color in axis_data:
        pygame.draw.line(surface, color, center, end, 3)
        pygame.draw.circle(surface, color, end, 4)
        text = font.render(label, True, color)
        surface.blit(text, (end[0] + 6, end[1] - 8))


def sorted_edges(rotated_vertices):
    return sorted(CUBE_EDGES, key=lambda edge: rotated_vertices[edge[0]][2] + rotated_vertices[edge[1]][2])


def draw_cube(surface, vertices_2d, rotated_vertices, color):
    for start, end in sorted_edges(rotated_vertices):
        z_average = (rotated_vertices[start][2] + rotated_vertices[end][2]) / 2
        brightness = max(0.45, min(1.0, 0.7 + z_average * 0.16))
        shaded = tuple(int(channel * brightness) for channel in color)
        width = 2 if z_average < 0 else 4
        pygame.draw.line(surface, shaded, vertices_2d[start], vertices_2d[end], width)

    for index, point in enumerate(vertices_2d):
        z = rotated_vertices[index][2]
        radius = 4 if z < 0 else 6
        pygame.draw.circle(surface, EDGE_COLOR, point, radius)


def draw_formula(surface, font, rect, lines):
    y = rect.bottom - 94
    for line in lines:
        y = draw_text(surface, font, line, rect.x + 18, y, MUTED_TEXT)


def draw_status(surface, font, angle_x, angle_y, zoom, camera_distance):
    controls = [
        "Drag: rotate",
        "Wheel: zoom",
        "Arrow keys: rotate",
        "W/S: perspective distance",
        "R: reset",
    ]

    x = 24
    y = HEIGHT - 116
    y = draw_text(surface, font, "Controls", x, y)
    for item in controls:
        y = draw_text(surface, font, item, x, y, MUTED_TEXT)

    stats = [
        f"rotation x: {math.degrees(angle_x):6.1f}",
        f"rotation y: {math.degrees(angle_y):6.1f}",
        f"zoom:       {zoom:6.2f}",
        f"camera d:   {camera_distance:6.2f}",
    ]
    y = HEIGHT - 98
    for item in stats:
        y = draw_text(surface, font, item, WIDTH - 230, y, MUTED_TEXT)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Projection Types: Orthographic and Perspective")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 16)
    title_font = pygame.font.SysFont("Segoe UI", 24, bold=True)
    main_title_font = pygame.font.SysFont("Segoe UI", 30, bold=True)

    angle_x = math.radians(22)
    angle_y = math.radians(-34)
    angle_z = math.radians(0)
    zoom = 1.0
    camera_distance = 4.0
    dragging = False
    last_mouse = (0, 0)

    left_panel = pygame.Rect(24, 86, 552, 500)
    right_panel = pygame.Rect(624, 86, 552, 500)
    left_center = (left_panel.centerx, left_panel.centery + 28)
    right_center = (right_panel.centerx, right_panel.centery + 28)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_r:
                    angle_x = math.radians(22)
                    angle_y = math.radians(-34)
                    angle_z = 0
                    zoom = 1.0
                    camera_distance = 4.0
                elif event.key == pygame.K_LEFT:
                    angle_y -= math.radians(4)
                elif event.key == pygame.K_RIGHT:
                    angle_y += math.radians(4)
                elif event.key == pygame.K_UP:
                    angle_x -= math.radians(4)
                elif event.key == pygame.K_DOWN:
                    angle_x += math.radians(4)
                elif event.key == pygame.K_w:
                    camera_distance = min(9.0, camera_distance + 0.2)
                elif event.key == pygame.K_s:
                    camera_distance = max(2.4, camera_distance - 0.2)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    last_mouse = event.pos
                elif event.button == 4:
                    zoom = min(2.2, zoom * 1.08)
                elif event.button == 5:
                    zoom = max(0.55, zoom / 1.08)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                dx = event.pos[0] - last_mouse[0]
                dy = event.pos[1] - last_mouse[1]
                angle_y += dx * 0.01
                angle_x += dy * 0.01
                last_mouse = event.pos

        scale = 115 * zoom
        rotated_vertices = [rotate_point(vertex, angle_x, angle_y, angle_z) for vertex in CUBE_VERTICES]

        ortho_points = [project_orthographic(vertex, left_center, scale) for vertex in rotated_vertices]
        perspective_points = [
            project_perspective(vertex, right_center, scale, camera_distance)
            for vertex in rotated_vertices
        ]

        rotated_axes = [
            rotate_point((1.6, 0, 0), angle_x, angle_y, angle_z),
            rotate_point((0, 1.6, 0), angle_x, angle_y, angle_z),
            rotate_point((0, 0, 1.6), angle_x, angle_y, angle_z),
        ]
        ortho_axes = [project_orthographic(axis, left_center, scale) for axis in rotated_axes]
        perspective_axes = [
            project_perspective(axis, right_center, scale, camera_distance)
            for axis in rotated_axes
        ]

        screen.fill(BG_COLOR)
        draw_text(screen, main_title_font, "Projection Effects", 24, 24)
        draw_text(
            screen,
            font,
            "The same rotating cube is converted from 3D coordinates to a 2D screen in two different ways.",
            24,
            58,
            MUTED_TEXT,
        )

        draw_panel(
            screen,
            left_panel,
            "Orthographic Projection",
            "Parallel projectors: object size does not change with depth.",
            font,
            title_font,
        )
        draw_panel(
            screen,
            right_panel,
            "Perspective Projection",
            "Projectors meet at the eye point: farther edges appear smaller.",
            font,
            title_font,
        )

        draw_grid(screen, left_center, 205)
        draw_grid(screen, right_center, 205)
        draw_axes(screen, left_center, ortho_axes, font)
        draw_axes(screen, right_center, perspective_axes, font)
        draw_cube(screen, ortho_points, rotated_vertices, ORTHO_COLOR)
        draw_cube(screen, perspective_points, rotated_vertices, PERSPECTIVE_COLOR)

        draw_formula(
            screen,
            font,
            left_panel,
            [
                "Formula: x' = x, y' = y",
                "Depth z is kept for ordering only.",
                "Useful in CAD and technical drawings.",
            ],
        )
        draw_formula(
            screen,
            font,
            right_panel,
            [
                "Formula: x' = x * d / (d - z)",
                "         y' = y * d / (d - z)",
                "Useful for realistic camera views.",
            ],
        )
        draw_status(screen, font, angle_x, angle_y, zoom, camera_distance)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
