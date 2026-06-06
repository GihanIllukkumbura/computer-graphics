"""
Interactive Illumination GUI
============================

Demonstrates ambient, diffuse, and specular illumination on a sphere using
the Phong lighting model.

Controls:
  - Drag inside the light ring: move the light direction
  - A / D / S: toggle ambient, diffuse, and specular components
  - 1 / 2: ambient intensity down / up
  - 3 / 4: diffuse intensity down / up
  - 5 / 6: specular intensity down / up
  - 7 / 8: shininess down / up
  - R: reset
  - Esc / Q: quit
"""

import math
import pygame
import numpy as np


WIDTH, HEIGHT = 1180, 760
BG_COLOR = (245, 247, 250)
PANEL_COLOR = (255, 255, 255)
TEXT_COLOR = (20, 27, 38)
MUTED_TEXT = (94, 103, 115)
GRID_COLOR = (226, 232, 240)
AMBIENT_COLOR = (67, 97, 238)
DIFFUSE_COLOR = (26, 140, 92)
SPECULAR_COLOR = (204, 112, 34)

SPHERE_SIZE = 420


def normalize(vector):
    length = float(np.linalg.norm(vector))
    if length == 0:
        return vector
    return vector / length


def clamp01(value):
    return max(0.0, min(1.0, value))


def draw_text(surface, font, text, x, y, color=TEXT_COLOR):
    label = font.render(text, True, color)
    surface.blit(label, (x, y))
    return y + font.get_linesize()


def draw_panel(surface, rect):
    pygame.draw.rect(surface, PANEL_COLOR, rect, border_radius=8)
    pygame.draw.rect(surface, (210, 218, 229), rect, 1, border_radius=8)


def build_sphere_surface(settings):
    radius = SPHERE_SIZE // 2
    y_grid, x_grid = np.mgrid[-radius:radius, -radius:radius]
    x = x_grid / radius
    y = -y_grid / radius
    r2 = x * x + y * y
    mask = r2 <= 1.0

    z = np.zeros_like(x)
    z[mask] = np.sqrt(1.0 - r2[mask])

    normals = np.dstack((x, y, z))
    light = normalize(np.array(settings["light"], dtype=np.float32))

    ndotl = np.maximum(0.0, normals[:, :, 0] * light[0] + normals[:, :, 1] * light[1] + normals[:, :, 2] * light[2])
    reflection = 2.0 * ndotl[:, :, None] * normals - light
    rdotv = np.maximum(0.0, reflection[:, :, 2])

    ambient = settings["ambient"] if settings["use_ambient"] else 0.0
    diffuse = settings["diffuse"] * ndotl if settings["use_diffuse"] else np.zeros_like(ndotl)
    specular = (
        settings["specular"] * np.power(rdotv, settings["shininess"])
        if settings["use_specular"]
        else np.zeros_like(rdotv)
    )

    base_color = np.array([0.16, 0.47, 0.78], dtype=np.float32)
    warm_light = np.array([1.0, 0.94, 0.82], dtype=np.float32)
    color = base_color * (ambient + diffuse[:, :, None]) + warm_light * specular[:, :, None]

    rim = np.power(1.0 - np.maximum(0.0, z), 2.2) * 0.16
    color += rim[:, :, None] * np.array([0.18, 0.30, 0.55], dtype=np.float32)
    color = np.clip(color, 0.0, 1.0)
    color[~mask] = np.array([245, 247, 250], dtype=np.float32) / 255.0

    image = (color * 255).astype(np.uint8)
    return pygame.surfarray.make_surface(np.transpose(image, (1, 0, 2)))


def draw_component_bar(surface, font, label, value, x, y, color, enabled=True, display_value=None):
    text_color = TEXT_COLOR if enabled else (150, 156, 166)
    draw_text(surface, font, label, x, y, text_color)
    pygame.draw.rect(surface, GRID_COLOR, (x, y + 24, 260, 12), border_radius=6)
    fill_width = int(260 * clamp01(value))
    if fill_width > 0:
        pygame.draw.rect(surface, color if enabled else (170, 174, 181), (x, y + 24, fill_width, 12), border_radius=6)
    display_value = value if display_value is None else display_value
    value_label = font.render(f"{display_value:.2f}", True, MUTED_TEXT)
    surface.blit(value_label, (x + 272, y + 17))


def draw_toggle(surface, font, label, x, y, enabled, color):
    box = pygame.Rect(x, y + 2, 20, 20)
    pygame.draw.rect(surface, color if enabled else (225, 229, 235), box, border_radius=4)
    pygame.draw.rect(surface, (165, 174, 186), box, 1, border_radius=4)
    if enabled:
        pygame.draw.line(surface, (255, 255, 255), (x + 5, y + 12), (x + 9, y + 17), 3)
        pygame.draw.line(surface, (255, 255, 255), (x + 9, y + 17), (x + 16, y + 6), 3)
    draw_text(surface, font, label, x + 30, y, TEXT_COLOR if enabled else MUTED_TEXT)


def draw_light_control(surface, font, center, light, radius=72):
    pygame.draw.circle(surface, (237, 241, 247), center, radius)
    pygame.draw.circle(surface, (190, 200, 214), center, radius, 2)
    pygame.draw.line(surface, GRID_COLOR, (center[0] - radius, center[1]), (center[0] + radius, center[1]), 1)
    pygame.draw.line(surface, GRID_COLOR, (center[0], center[1] - radius), (center[0], center[1] + radius), 1)

    marker = (
        int(center[0] + light[0] * radius),
        int(center[1] - light[1] * radius),
    )
    pygame.draw.line(surface, (108, 119, 135), center, marker, 2)
    pygame.draw.circle(surface, (236, 179, 52), marker, 12)
    pygame.draw.circle(surface, (120, 89, 16), marker, 12, 2)

    y = center[1] + radius + 18
    draw_text(surface, font, "Drag the dot to move light", center[0] - 104, y, MUTED_TEXT)


def draw_formula(surface, font, x, y):
    lines = [
        "Phong model",
        "I = ka Ia + kd Il max(N . L, 0)",
        "    + ks Il max(R . V, 0)^n",
    ]
    for index, line in enumerate(lines):
        color = TEXT_COLOR if index == 0 else MUTED_TEXT
        y = draw_text(surface, font, line, x, y, color)


def update_light_from_mouse(settings, mouse_pos, center):
    dx = (mouse_pos[0] - center[0]) / 72.0
    dy = -(mouse_pos[1] - center[1]) / 72.0
    dx = clamp01((dx + 1.0) / 2.0) * 2.0 - 1.0
    dy = clamp01((dy + 1.0) / 2.0) * 2.0 - 1.0
    z = math.sqrt(max(0.15, 1.0 - dx * dx - dy * dy))
    settings["light"] = normalize(np.array([dx, dy, z], dtype=np.float32))


def reset_settings():
    return {
        "use_ambient": True,
        "use_diffuse": True,
        "use_specular": True,
        "ambient": 0.25,
        "diffuse": 0.82,
        "specular": 0.55,
        "shininess": 28,
        "light": normalize(np.array([-0.45, 0.48, 0.75], dtype=np.float32)),
    }


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Illumination Effects: Ambient, Diffuse, Specular")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 16)
    title_font = pygame.font.SysFont("Segoe UI", 30, bold=True)
    panel_title_font = pygame.font.SysFont("Segoe UI", 24, bold=True)

    settings = reset_settings()
    sphere_surface = build_sphere_surface(settings)
    needs_render = False
    dragging_light = False

    sphere_rect = pygame.Rect(44, 132, SPHERE_SIZE, SPHERE_SIZE)
    controls_rect = pygame.Rect(520, 88, 620, 628)
    light_center = (990, 326)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_r:
                    settings = reset_settings()
                    needs_render = True
                elif event.key == pygame.K_a:
                    settings["use_ambient"] = not settings["use_ambient"]
                    needs_render = True
                elif event.key == pygame.K_d:
                    settings["use_diffuse"] = not settings["use_diffuse"]
                    needs_render = True
                elif event.key == pygame.K_s:
                    settings["use_specular"] = not settings["use_specular"]
                    needs_render = True
                elif event.key == pygame.K_1:
                    settings["ambient"] = max(0.0, settings["ambient"] - 0.05)
                    needs_render = True
                elif event.key == pygame.K_2:
                    settings["ambient"] = min(1.0, settings["ambient"] + 0.05)
                    needs_render = True
                elif event.key == pygame.K_3:
                    settings["diffuse"] = max(0.0, settings["diffuse"] - 0.05)
                    needs_render = True
                elif event.key == pygame.K_4:
                    settings["diffuse"] = min(1.25, settings["diffuse"] + 0.05)
                    needs_render = True
                elif event.key == pygame.K_5:
                    settings["specular"] = max(0.0, settings["specular"] - 0.05)
                    needs_render = True
                elif event.key == pygame.K_6:
                    settings["specular"] = min(1.25, settings["specular"] + 0.05)
                    needs_render = True
                elif event.key == pygame.K_7:
                    settings["shininess"] = max(2, settings["shininess"] - 2)
                    needs_render = True
                elif event.key == pygame.K_8:
                    settings["shininess"] = min(96, settings["shininess"] + 2)
                    needs_render = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                distance = math.dist(event.pos, light_center)
                if distance <= 84:
                    dragging_light = True
                    update_light_from_mouse(settings, event.pos, light_center)
                    needs_render = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_light = False
            elif event.type == pygame.MOUSEMOTION and dragging_light:
                update_light_from_mouse(settings, event.pos, light_center)
                needs_render = True

        if needs_render:
            sphere_surface = build_sphere_surface(settings)
            needs_render = False

        screen.fill(BG_COLOR)
        draw_text(screen, title_font, "Illumination Effects", 36, 28)
        draw_text(
            screen,
            font,
            "Move the light and change each term to see how the final shaded object is built.",
            38,
            66,
            MUTED_TEXT,
        )

        draw_panel(screen, pygame.Rect(28, 88, 464, 628))
        draw_text(screen, panel_title_font, "", 52, 106)
        pygame.draw.rect(screen, (236, 240, 246), sphere_rect.inflate(24, 24), border_radius=8)
        screen.blit(sphere_surface, sphere_rect.topleft)

        light_projection = (
            int(sphere_rect.centerx + settings["light"][0] * 145),
            int(sphere_rect.centery - settings["light"][1] * 145),
        )
        pygame.draw.line(screen, (236, 179, 52), light_projection, sphere_rect.center, 3)
        pygame.draw.circle(screen, (236, 179, 52), light_projection, 10)

        draw_panel(screen, controls_rect)
        draw_text(screen, panel_title_font, "Lighting Controls", controls_rect.x + 28, controls_rect.y + 22)

        draw_toggle(screen, font, "Ambient light", controls_rect.x + 30, 146, settings["use_ambient"], AMBIENT_COLOR)
        draw_toggle(screen, font, "Diffuse reflection", controls_rect.x + 30, 178, settings["use_diffuse"], DIFFUSE_COLOR)
        draw_toggle(screen, font, "Specular highlight", controls_rect.x + 30, 210, settings["use_specular"], SPECULAR_COLOR)

        draw_component_bar(
            screen,
            font,
            "Ambient intensity",
            settings["ambient"],
            controls_rect.x + 30,
            266,
            AMBIENT_COLOR,
            settings["use_ambient"],
        )
        draw_component_bar(
            screen,
            font,
            "Diffuse intensity",
            settings["diffuse"] / 1.25,
            controls_rect.x + 30,
            330,
            DIFFUSE_COLOR,
            settings["use_diffuse"],
            settings["diffuse"],
        )
        draw_component_bar(
            screen,
            font,
            "Specular intensity",
            settings["specular"] / 1.25,
            controls_rect.x + 30,
            394,
            SPECULAR_COLOR,
            settings["use_specular"],
            settings["specular"],
        )
        draw_component_bar(
            screen,
            font,
            f"Shininess exponent: {settings['shininess']}",
            settings["shininess"] / 96.0,
            controls_rect.x + 30,
            458,
            SPECULAR_COLOR,
            settings["use_specular"],
            settings["shininess"],
        )

        draw_light_control(screen, font, light_center, settings["light"])
        draw_formula(screen, font, controls_rect.x + 30, 546)
        draw_text(screen, font, "A/D/S toggle components", controls_rect.x + 30, 622, MUTED_TEXT)
        draw_text(screen, font, "1-8 adjust intensities and shininess", controls_rect.x + 30, 644, MUTED_TEXT)

        draw_text(screen, font, "R: reset   Q/Esc: quit", 38, HEIGHT - 44, MUTED_TEXT)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
