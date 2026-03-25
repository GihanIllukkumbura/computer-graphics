"""
Tutorial 01: Point Drawer
=========================
Based on: PointDrawer.java

Demonstrates the most fundamental operation in computer graphics:
plotting a single pixel (point) on the screen.

This is the building block for ALL rasterization algorithms -
every line, circle, and shape is ultimately just a collection of points.

Controls:
    - Click anywhere to plot a point
    - ESC to exit
"""

import pygame
import sys

# ============================================================
# Configuration
# ============================================================
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
POINT_SIZE = 5
BG_COLOR = (255, 255, 255)       # White background
POINT_COLOR = (255, 0, 0)        # Red points
AXIS_COLOR = (200, 200, 200)     # Light grey axes
TEXT_COLOR = (0, 0, 0)           # Black text
GRID_COLOR = (240, 240, 240)     # Very light grey grid


def screen_to_cartesian(sx, sy, height):
    """Convert screen coordinates (top-left origin) to
    Cartesian coordinates (center origin)."""
    width = WINDOW_WIDTH
    return sx - width // 2, height // 2 - sy


def cartesian_to_screen(cx, cy, height):
    """Convert Cartesian coordinates (center origin) to
    screen coordinates (top-left origin)."""
    width = WINDOW_WIDTH
    return width // 2 + cx, height // 2 - cy


def draw_point(surface, x, y, color=POINT_COLOR, size=POINT_SIZE):
    """
    Plot a point at Cartesian coordinates (x, y).

    This mirrors the Java code:
        g.fillOval(drawX, drawY, pointSize, pointSize);

    In Pygame we use draw.circle for a cleaner look.
    """
    # Convert from Cartesian to screen coordinates
    sx, sy = cartesian_to_screen(x, y, surface.get_height())
    # Center the dot on the coordinate
    pygame.draw.circle(surface, color, (int(sx), int(sy)), size // 2)


def draw_point_label(surface, font, x, y, color=TEXT_COLOR):
    """Draw coordinate text near a plotted point."""
    sx, sy = cartesian_to_screen(x, y, surface.get_height())
    label = font.render(f"({x}, {y})", True, color)
    surface.blit(label, (int(sx) + 8, int(sy) - 20))


def draw_axes(surface):
    """Draw light reference axes through the center."""
    w, h = surface.get_size()
    cx, cy = w // 2, h // 2
    # X axis (y = 0)
    pygame.draw.line(surface, AXIS_COLOR, (0, cy), (w, cy), 1)
    # Y axis (x = 0)
    pygame.draw.line(surface, AXIS_COLOR, (cx, 0), (cx, h), 1)


def draw_grid(surface, spacing=50):
    """Draw a light background grid for reference."""
    w, h = surface.get_size()
    cx, cy = w // 2, h // 2

    for x in range(cx % spacing, w, spacing):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, h), 1)
    for y in range(cy % spacing, h, spacing):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (w, y), 1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tutorial 01: Point Drawer")
    font = pygame.font.SysFont("Consolas", 16)
    clock = pygame.time.Clock()

    # List of plotted points (Cartesian coords)
    points = []

    # Initial demo point relative to origin at the center.
    points.append((100, 100))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    points.clear()  # Clear all points
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Convert click position to Cartesian and store
                mx, my = event.pos
                cx, cy = screen_to_cartesian(mx, my, WINDOW_HEIGHT)
                points.append((cx, cy))

        # --- Drawing ---
        screen.fill(BG_COLOR)
        draw_grid(screen)
        draw_axes(screen)

        # Plot all stored points
        for px, py in points:
            draw_point(screen, px, py)
            draw_point_label(screen, font, px, py)

        # HUD text
        title = font.render("Point Drawer — Click to plot points | C = Clear | ESC = Quit", True, TEXT_COLOR)
        screen.blit(title, (10, 10))

        if points:
            last = points[-1]
            coord_text = font.render(f"Last point: ({last[0]}, {last[1]})  |  Total: {len(points)}", True, TEXT_COLOR)
            screen.blit(coord_text, (10, 32))

        origin_text = font.render("Origin: (0, 0)", True, TEXT_COLOR)
        screen.blit(origin_text, (10, 54))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
