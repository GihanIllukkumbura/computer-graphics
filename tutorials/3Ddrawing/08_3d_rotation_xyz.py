"""
3D Rotation around X, Y, Z Axes Tutorial - Interactive GUI

Demonstrates composition of rotations around X, Y, Z axes with live matrix display.
Controls:
  - Left Click + Drag: Rotate view
  - Mouse Wheel: Zoom in/out
  - +/=/-: Zoom in/out (keyboard)
  - Left/Right Arrow: X-rotation
  - Up/Down Arrow: Y-rotation
  - X/x, Y/y, Z/z: Individual axis control
  - Shift+Left/Right: Pivot X
  - Ctrl+Up/Down: Pivot Z (Up/Down also does Y without Ctrl)
  - Shift: Fine adjustment (2.5°)
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


class RotationXYZ3D:
    """Interactive 3D rotation around XYZ axes tutorial."""

    def __init__(self, width: int = 1000, height: int = 700):
        pygame.init()
        self.width = width
        self.height = height
        self.display = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Rotation around X, Y, Z Axes Tutorial")

        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0
        self.px = 0.0
        self.py = 0.0
        self.pz = 0.0
        
        # View rotation (mouse-controlled)
        self.view_angle_x = 0.0
        self.view_angle_y = 0.0
        self.zoom = 1.0
        
        # Mouse tracking
        self.mouse_dragging = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.reset_button_rect = (20, 250, 150, 350)

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
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0
        self.px = 0.0
        self.py = 0.0
        self.pz = 0.0
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
                step = 2.5 if (mods & pygame.KMOD_SHIFT) else 5.0
                pivot_step = step * 0.1
                
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return False
                if event.key == pygame.K_r:
                    self.reset_all()
                # LEFT/RIGHT for angle_x
                if event.key == pygame.K_LEFT:
                    self.angle_x -= step
                if event.key == pygame.K_RIGHT:
                    self.angle_x += step
                # UP/DOWN for angle_y
                if event.key == pygame.K_DOWN:
                    if mods & pygame.KMOD_CTRL:
                        self.pz -= pivot_step
                    else:
                        self.angle_y -= step
                if event.key == pygame.K_UP:
                    if mods & pygame.KMOD_CTRL:
                        self.pz += pivot_step
                    else:
                        self.angle_y += step
                # X/Y/Z keys still work for individual angle control
                if event.key == pygame.K_x:
                    if mods & pygame.KMOD_SHIFT:
                        self.angle_x += step
                    else:
                        self.angle_x -= step
                if event.key == pygame.K_y:
                    if mods & pygame.KMOD_SHIFT:
                        self.angle_y += step
                    else:
                        self.angle_y -= step
                if event.key == pygame.K_z:
                    if mods & pygame.KMOD_SHIFT:
                        self.angle_z += step
                    else:
                        self.angle_z -= step
                # Pivot controls with SHIFT
                if mods & pygame.KMOD_SHIFT:
                    if event.key == pygame.K_LEFT:
                        self.px -= pivot_step
                    if event.key == pygame.K_RIGHT:
                        self.px += pivot_step
                    if event.key == pygame.K_DOWN:
                        self.py -= pivot_step
                    if event.key == pygame.K_UP:
                        self.py += pivot_step
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self.zoom = min(3.0, self.zoom + 0.1)
                if event.key == pygame.K_MINUS:
                    self.zoom = max(0.3, self.zoom - 0.1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
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

        # Rotated cube around pivot (cyan wireframe)
        glPushMatrix()
        Rx = Matrix4.rotation_x(math.radians(self.angle_x))
        Ry = Matrix4.rotation_y(math.radians(self.angle_y))
        Rz = Matrix4.rotation_z(math.radians(self.angle_z))
        R_composed = Matrix4.compose([Rx, Ry, Rz])
        M = apply_transformation_with_pivot(R_composed, (self.px, self.py, self.pz))
        GLHelpers.apply_matrix_to_gl(M)
        GLHelpers.draw_cube_wireframe(Cube.vertices(), color=(0.0, 1.0, 1.0), line_width=2.0)
        glPopMatrix()

        # Draw pivot point
        glPushMatrix()
        glTranslatef(self.px, self.py, self.pz)
        glColor3f(1.0, 0.0, 0.0)
        self.draw_point()
        glPopMatrix()

        self.render_hud(M)

    def draw_point(self) -> None:
        """Draw a small point at origin."""
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
        """Render HUD with key mappings in top-right corner."""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)

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
        glLineWidth(1.0)

        hud_info = [
            "3D Rotation XYZ Tutorial",
            "",
            f"Angles: X={self.angle_x:7.1f}  Y={self.angle_y:7.1f}  Z={self.angle_z:7.1f}",
            f"Pivot: ({self.px:7.2f}, {self.py:7.2f}, {self.pz:7.2f})",
            "",
            "Matrix (T(p) * Rxyz * T(-p)):",
            GLHelpers.matrix_to_string(matrix, precision=2),
        ]

        y_offset = 20
        for line in hud_info:
            if not line:
                y_offset += 16
                continue

            for subline in line.splitlines():
                self.render_text_2d(subline, 20, y_offset, color=(1.0, 1.0, 1.0))
                y_offset += 16

        # Axis labels inside the left panel
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.render_text_2d("AXES:", self.reset_button_rect[0] + 8, self.reset_button_rect[1] + 18, color=(0.95, 0.95, 0.95))
        self.render_text_2d("X - Red", self.reset_button_rect[0] + 8, self.reset_button_rect[1] + 34, color=(1.0, 0.2, 0.2))
        self.render_text_2d("Y - Green", self.reset_button_rect[0] + 8, self.reset_button_rect[1] + 50, color=(0.2, 1.0, 0.2))
        self.render_text_2d("Z - Blue", self.reset_button_rect[0] + 8, self.reset_button_rect[1] + 66, color=(0.2, 0.4, 1.0))
        self.render_text_2d("RESET", self.reset_button_rect[0] + 28, self.reset_button_rect[1] + 88, color=(0.95, 0.95, 0.95))
        glDisable(GL_BLEND)

        # Draw key mappings in top-right corner
        self.render_key_mappings_top_right()

        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def render_key_mappings_top_right(self) -> None:
        """Render key mappings in top-right corner as a colored panel."""
        key_mapping_lines = [
            "=== KEY MAPPINGS ===",
            "",
            "MOUSE CONTROLS:",
            "  Click+Drag: Rotate view",
            "  Scroll Wheel: Zoom",
            "",
            "ROTATION CONTROL:",
            "  Left/Right: X-rotation",
            "  Up/Down: Y-rotation",
            "  X/x, Y/y, Z/z: Axis control",
            "  Shift+Left/Right: Pivot X",
            "  Ctrl+Up/Down: Pivot Z",
            "",
            "GENERAL:",
            "  +/-: Zoom in/out",
            "  Shift: Fine (2.5°)",
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
    app = RotationXYZ3D()
    app.run()
