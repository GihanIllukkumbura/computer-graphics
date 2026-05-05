"""
3D Scaling Tutorial - Interactive GUI

Demonstrates scaling around a pivot point in 3D with live matrix display.
Controls:
  - Left Click + Drag: Rotate view
  - Mouse Wheel: Zoom in/out
  - Left/Right Arrow: Scale factor
  - Up/Down Arrow: Pivot Y axis
  - Ctrl+Up/Down: Pivot Z axis
  - Shift+Left/Right: Pivot X axis
  - +/-: Zoom in/out (keyboard)
  - Shift: Fine adjustment (0.05)
  - R: Reset
  - Q/ESC: Quit
"""

import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10
import numpy as np
import math

sys.path.insert(0, '.')
from three_d_utils import Matrix4, Cube, GLHelpers, apply_transformation_with_pivot

# Initialize GLUT for text rendering
try:
    glutInit()
except:
    pass


class Scaling3D:
    """Interactive 3D scaling tutorial."""

    def __init__(self, width: int = 1000, height: int = 700):
        pygame.init()
        self.width = width
        self.height = height
        self.display = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Scaling Tutorial")

        self.px = 0.0
        self.py = 0.0
        self.pz = 0.0
        self.scale = 1.0

        # View rotation (mouse-controlled)
        self.view_angle_x = 0.0
        self.view_angle_y = 0.0
        self.zoom = 1.0
        
        # Mouse tracking
        self.mouse_dragging = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.reset_button_rect = (20, 320, 120, 350)

        self.setup_gl()

    def setup_gl(self) -> None:
        """Initialize OpenGL settings."""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glClearColor(0.1, 0.1, 0.15, 1.0)
        GLHelpers.setup_projection(self.width, self.height)

    def reset_all(self) -> None:
        """Reset all parameters to defaults."""
        self.px = self.py = self.pz = 0.0
        self.scale = 1.0
        self.view_angle_x = 0.0
        self.view_angle_y = 0.0
        self.zoom = 1.0

    def is_point_in_rect(self, point: tuple, rect: tuple) -> bool:
        """Check if point (x, y) is inside rectangle (x1, y1, x2, y2)."""
        x, y = point
        x1, y1, x2, y2 = rect
        return x1 <= x <= x2 and y1 <= y <= y2

    def handle_events(self) -> bool:
        """Handle user input; return False if quit requested."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                step = 0.05 if (mods & pygame.KMOD_SHIFT) else 0.1
                
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return False
                if event.key == pygame.K_r:
                    self.reset_all()
                if event.key == pygame.K_LEFT:
                    self.scale = max(0.1, self.scale - step)
                if event.key == pygame.K_RIGHT:
                    self.scale += step
                if event.key == pygame.K_DOWN:
                    if mods & pygame.KMOD_CTRL:
                        self.pz -= step
                    else:
                        self.py -= step
                if event.key == pygame.K_UP:
                    if mods & pygame.KMOD_CTRL:
                        self.pz += step
                    else:
                        self.py += step
                if mods & pygame.KMOD_SHIFT:
                    if event.key == pygame.K_LEFT:
                        self.px -= step
                    if event.key == pygame.K_RIGHT:
                        self.px += step
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self.zoom = min(3.0, self.zoom + 0.1)
                if event.key == pygame.K_MINUS:
                    self.zoom = max(0.3, self.zoom - 0.1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_dragging = True
                    self.last_mouse_x = event.pos[0]
                    self.last_mouse_y = event.pos[1]
                    if self.is_point_in_rect(event.pos, self.reset_button_rect):
                        self.reset_all()
                        self.mouse_dragging = False
                elif event.button == 4:  # Scroll wheel up - zoom in
                    self.zoom = min(3.0, self.zoom * 1.1)
                elif event.button == 5:  # Scroll wheel down - zoom out
                    self.zoom = max(0.3, self.zoom / 1.1)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_dragging:
                    dx = event.pos[0] - self.last_mouse_x
                    dy = event.pos[1] - self.last_mouse_y
                    self.view_angle_y += dx * 0.5
                    self.view_angle_x += dy * 0.5
                    self.last_mouse_x = event.pos[0]
                    self.last_mouse_y = event.pos[1]
        return True

    def render(self) -> None:
        """Render the scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Setup view with mouse-controlled rotation
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -10)
        glScalef(self.zoom, self.zoom, self.zoom)
        glRotatef(self.view_angle_x, 1, 0, 0)
        glRotatef(self.view_angle_y, 0, 1, 0)
        glTranslatef(-1.5, -1.5, -1.5)

        # Draw reference axes and grid
        GLHelpers.draw_grid(size=6.0, step=0.5)
        GLHelpers.draw_axes(length=1.0)

        # Original cube (white wireframe)
        glPushMatrix()
        GLHelpers.draw_cube_wireframe(Cube.vertices(), color=(1.0, 1.0, 1.0), line_width=1.5)
        glPopMatrix()

        # Scaled cube around pivot (cyan wireframe)
        glPushMatrix()
        S = Matrix4.scaling(self.scale, self.scale, self.scale)
        M = apply_transformation_with_pivot(S, (self.px, self.py, self.pz))
        GLHelpers.apply_matrix_to_gl(M)
        GLHelpers.draw_cube_wireframe(Cube.vertices(), color=(0.0, 1.0, 1.0), line_width=2.0)
        glPopMatrix()

        # Draw pivot point as small sphere (red dot)
        glPushMatrix()
        glTranslatef(self.px, self.py, self.pz)
        glColor3f(1.0, 0.0, 0.0)
        self.draw_point()
        glPopMatrix()

        self.render_hud(M)

    def draw_point(self, size: float = 0.1) -> None:
        """Draw a small sphere at origin."""
        glPointSize(5.0)
        glBegin(GL_POINTS)
        glVertex3f(0.0, 0.0, 0.0)
        glEnd()

    def render_text_2d(self, text: str, x: float, y: float, color=(0.2, 1.0, 0.2)) -> None:
        """Render text at 2D position using GLUT."""
        glColor3f(*color)
        glRasterPos2f(x, y)
        
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

    def render_hud(self, matrix: np.ndarray) -> None:
        """Render HUD with matrix and controls information."""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)

        self.render_key_mappings()

        # Draw reset button background
        glColor3f(0.2, 0.5, 0.2)
        glBegin(GL_QUADS)
        glVertex2f(self.reset_button_rect[0], self.reset_button_rect[1])
        glVertex2f(self.reset_button_rect[2], self.reset_button_rect[1])
        glVertex2f(self.reset_button_rect[2], self.reset_button_rect[3])
        glVertex2f(self.reset_button_rect[0], self.reset_button_rect[3])
        glEnd()

        # Draw reset button border
        glColor3f(0.8, 1.0, 0.8)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.reset_button_rect[0], self.reset_button_rect[1])
        glVertex2f(self.reset_button_rect[2], self.reset_button_rect[1])
        glVertex2f(self.reset_button_rect[2], self.reset_button_rect[3])
        glVertex2f(self.reset_button_rect[0], self.reset_button_rect[3])
        glEnd()

        hud_info = [
            "3D Scaling Tutorial (around pivot)",
            "",
            f"Pivot: ({self.px:7.2f}, {self.py:7.2f}, {self.pz:7.2f})",
            f"Scale: {self.scale:7.2f}",
            f"View: X={self.view_angle_x:6.1f}° Y={self.view_angle_y:6.1f}°",
            "",
            "Matrix (T(p) * S * T(-p)):",
            GLHelpers.matrix_to_string(matrix, precision=2),
            "",
            "Controls:",
            "  Left/Right: Scale factor",
            "  Up/Down: Pivot Y, Ctrl+Up/Down: Pivot Z",
            "  Shift+Left/Right: Pivot X",
            "  Mouse Drag: Rotate view",
            "  Shift: Fine adjustment (0.05)",
            "  [RESET]: Reset all (click or R)",
            "  Q/ESC: Quit",
        ]

        y_offset = 20
        for line in hud_info:
            if not line:
                y_offset += 16
                continue

            for subline in line.splitlines():
                self.render_text_2d(subline, 20, y_offset, color=(1.0, 1.0, 1.0))
                y_offset += 16

        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def render_key_mappings(self) -> None:
        """Render key mappings in top-right corner as a colored panel."""
        key_mapping_lines = [
            "=== KEY MAPPINGS ===",
            "",
            "MOUSE CONTROLS:",
            "  Click+Drag: Rotate view",
            "  Scroll Wheel: Zoom",
            "",
            "SCALING CONTROL:",
            "  Left/Right Arrow: Scale",
            "  Shift+Left/Right: Pivot X",
            "  Up/Down Arrow: Pivot Y",
            "  Ctrl+Up/Down: Pivot Z",
            "",
            "GENERAL:",
            "  +/-: Zoom in/out",
            "  Shift: Fine (0.05)",
            "  R: Reset",
            "  Q/ESC: Quit",
        ]

        # Calculate panel dimensions
        box_width = 240
        box_height = len(key_mapping_lines) * 14 + 10
        box_x = self.width - box_width - 10
        box_y = 10

        # Draw semi-transparent background
        glColor4f(0.05, 0.15, 0.05, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(box_x, box_y)
        glVertex2f(box_x + box_width, box_y)
        glVertex2f(box_x + box_width, box_y + box_height)
        glVertex2f(box_x, box_y + box_height)
        glEnd()

        # Draw border
        glColor3f(0.2, 1.0, 0.2)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(box_x, box_y)
        glVertex2f(box_x + box_width, box_y)
        glVertex2f(box_x + box_width, box_y + box_height)
        glVertex2f(box_x, box_y + box_height)
        glEnd()
        glLineWidth(1.0)

        # Render text inside the box
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        text_y = box_y + 15
        for line in key_mapping_lines:
            if line.strip():  # Only render non-empty lines
                self.render_text_2d(line, box_x + 8, text_y, color=(0.2, 1.0, 0.2))
            text_y += 14
        
        glDisable(GL_BLEND)

    def run(self) -> None:
        """Main loop."""
        clock = pygame.time.Clock()
        running = True
        while running:
            running = self.handle_events()
            self.render()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    app = Scaling3D()
    app.run()
