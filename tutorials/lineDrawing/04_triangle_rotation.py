"""
Tutorial 04: Triangle Rotation (2D Transformations)
=====================================================
Based on: TriangleRotation.java

Demonstrates 2D geometric transformations:
  - Rotation of a triangle about an arbitrary pivot point
  - Uses the rotation matrix:
      x' = cos(θ)*(x - px) - sin(θ)*(y - py) + px
      y' = sin(θ)*(x - px) + cos(θ)*(y - py) + py

The Java version uses AffineTransform.rotate(). Here we implement
the rotation manually so students can see the matrix math.

Controls:
    - LEFT/RIGHT arrow keys to change rotation angle
    - Click to move the pivot point
    - R = Reset
    - ESC = Quit
"""

import pygame
import sys
import math

# ============================================================
# Configuration
# ============================================================
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BG_COLOR = (255, 255, 255)
ORIGINAL_COLOR = (0, 0, 255)     # Blue - original triangle
ROTATED_COLOR = (255, 0, 0)      # Red  - rotated triangle
PIVOT_COLOR = (0, 150, 0)        # Green - pivot point
TEXT_COLOR = (0, 0, 0)
GRID_COLOR = (240, 240, 240)


def rotate_point(x, y, pivot_x, pivot_y, angle_degrees):
    """
    Rotate point (x, y) around pivot (pivot_x, pivot_y) by angle_degrees.

    This is the manual equivalent of Java's:
        AffineTransform transform = new AffineTransform();
        transform.rotate(Math.toRadians(rotationDegrees), x1, y1);

    The rotation matrix:
        | cos(θ)  -sin(θ) |   | x - px |   | px |
        | sin(θ)   cos(θ) | × | y - py | + | py |
    """
    angle_rad = math.radians(angle_degrees)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # Translate to origin (relative to pivot)
    dx = x - pivot_x
    dy = y - pivot_y

    # Apply rotation
    new_x = cos_a * dx - sin_a * dy
    new_y = sin_a * dx + cos_a * dy

    # Translate back
    return new_x + pivot_x, new_y + pivot_y


def draw_triangle(surface, p1, p2, p3, color, width=2):
    """Draw a triangle given three vertices."""
    pygame.draw.line(surface, color, p1, p2, width)
    pygame.draw.line(surface, color, p2, p3, width)
    pygame.draw.line(surface, color, p3, p1, width)


def draw_grid(surface, spacing=50):
    """Draw a light background grid."""
    w, h = surface.get_size()
    for x in range(0, w, spacing):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, h), 1)
    for y in range(0, h, spacing):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (w, y), 1)


def draw_angle_arc(surface, pivot, angle, radius=40):
    """Draw an arc showing the rotation angle."""
    if abs(angle) < 1:
        return
    start_angle = 0
    end_angle = math.radians(-angle)
    if end_angle < start_angle:
        start_angle, end_angle = end_angle, start_angle

    rect = pygame.Rect(
        pivot[0] - radius, pivot[1] - radius,
        radius * 2, radius * 2
    )
    pygame.draw.arc(surface, PIVOT_COLOR, rect, start_angle, end_angle, 2)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tutorial 04: Triangle Rotation")
    font = pygame.font.SysFont("Consolas", 15)
    big_font = pygame.font.SysFont("Consolas", 20)
    clock = pygame.time.Clock()

    # Original triangle vertices (same as Java reference)
    tri_p1 = (200, 200)   # Fixed vertex / pivot
    tri_p2 = (300, 300)
    tri_p3 = (250, 150)

    # Pivot point (rotation centre) — starts at first vertex like Java
    pivot = list(tri_p1)

    # Rotation angle (degrees)
    rotation_angle = 45.0   # Same default as Java

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    rotation_angle = 45.0
                    pivot = list(tri_p1)
                elif event.key == pygame.K_LEFT:
                    rotation_angle -= 5
                elif event.key == pygame.K_RIGHT:
                    rotation_angle += 5
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pivot = list(event.pos)

        # --- Drawing ---
        screen.fill(BG_COLOR)
        draw_grid(screen)

        # Draw original triangle (blue)
        draw_triangle(screen, tri_p1, tri_p2, tri_p3, ORIGINAL_COLOR, 2)

        # Label original vertices
        for label, pt in [("P1", tri_p1), ("P2", tri_p2), ("P3", tri_p3)]:
            t = font.render(f"{label}{pt}", True, ORIGINAL_COLOR)
            screen.blit(t, (pt[0] + 5, pt[1] - 15))

        # Calculate rotated triangle
        r1 = rotate_point(tri_p1[0], tri_p1[1], pivot[0], pivot[1], rotation_angle)
        r2 = rotate_point(tri_p2[0], tri_p2[1], pivot[0], pivot[1], rotation_angle)
        r3 = rotate_point(tri_p3[0], tri_p3[1], pivot[0], pivot[1], rotation_angle)

        r1_int = (int(r1[0]), int(r1[1]))
        r2_int = (int(r2[0]), int(r2[1]))
        r3_int = (int(r3[0]), int(r3[1]))

        # Draw rotated triangle (red)
        draw_triangle(screen, r1_int, r2_int, r3_int, ROTATED_COLOR, 2)

        # Label rotated vertices
        for label, pt in [("P1'", r1_int), ("P2'", r2_int), ("P3'", r3_int)]:
            t = font.render(f"{label}{pt}", True, ROTATED_COLOR)
            screen.blit(t, (pt[0] + 5, pt[1] + 5))

        # Draw pivot point
        pygame.draw.circle(screen, PIVOT_COLOR, (int(pivot[0]), int(pivot[1])), 6)
        pygame.draw.circle(screen, (255, 255, 255), (int(pivot[0]), int(pivot[1])), 3)
        pivot_label = font.render(f"Pivot ({int(pivot[0])},{int(pivot[1])})", True, PIVOT_COLOR)
        screen.blit(pivot_label, (int(pivot[0]) + 10, int(pivot[1]) - 20))

        # Draw angle arc
        draw_angle_arc(screen, (int(pivot[0]), int(pivot[1])), rotation_angle)

        # HUD
        title = font.render(
            "Triangle Rotation — ←/→ = Angle | Click = Move Pivot | R = Reset | ESC = Quit",
            True, TEXT_COLOR)
        screen.blit(title, (10, 10))

        angle_text = big_font.render(f"Rotation: {rotation_angle:.1f}°", True, TEXT_COLOR)
        screen.blit(angle_text, (10, 35))

        # Legend
        pygame.draw.line(screen, ORIGINAL_COLOR, (10, WINDOW_HEIGHT - 50), (30, WINDOW_HEIGHT - 50), 3)
        screen.blit(font.render("Original Triangle", True, ORIGINAL_COLOR), (35, WINDOW_HEIGHT - 57))
        pygame.draw.line(screen, ROTATED_COLOR, (10, WINDOW_HEIGHT - 30), (30, WINDOW_HEIGHT - 30), 3)
        screen.blit(font.render("Rotated Triangle", True, ROTATED_COLOR), (35, WINDOW_HEIGHT - 37))

        # Show the rotation matrix
        rad = math.radians(rotation_angle)
        mat_text = [
            "Rotation Matrix:",
            f"| {math.cos(rad):+.3f}  {-math.sin(rad):+.3f} |",
            f"| {math.sin(rad):+.3f}  {math.cos(rad):+.3f}  |",
        ]
        for i, line in enumerate(mat_text):
            t = font.render(line, True, TEXT_COLOR)
            screen.blit(t, (WINDOW_WIDTH - 250, WINDOW_HEIGHT - 80 + i * 18))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
