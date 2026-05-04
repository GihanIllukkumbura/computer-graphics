"""
3D Composite Transformation Tutorial - Interactive GUI

Demonstrates a clear composite transform using scaling and XYZ rotations around a pivot:
M = T(pivot) * Rz * Ry * Rx * S * T(-pivot)

Controls:
  - Left Click + Drag: Rotate camera view
  - Mouse Wheel or +/-: Zoom in/out
  - Left/Right: Rotate X
  - Up/Down: Rotate Y
  - Z/z: Rotate Z (+/-)
  - A/D: Scale X (-/+)
  - W/S: Scale Y (+/-)
  - E/C: Scale Z (+/-)
  - Shift + Arrows: Move pivot X/Y
  - Ctrl + Up/Down: Move pivot Z
  - Shift: Fine adjustment
  - R: Reset
  - Q/ESC: Quit
"""

import sys
import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10, glutBitmapCharacter, glutInit
import numpy as np

sys.path.insert(0, ".")
from three_d_utils import Matrix4, Cube, GLHelpers, apply_transformation_with_pivot


class CompositeTransformation3D:
    """Interactive 3D composite transformation tutorial."""

    def __init__(self, width: int = 1100, height: int = 720):
        pygame.init()
        self.width = width
        self.height = height
        self.display = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Composite Transformation Tutorial")

        # Initialize GLUT text rendering after OpenGL context creation
        try:
            glutInit()
        except Exception:
            pass

        # Transformation parameters
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0
        self.sx = 1.0
        self.sy = 1.0
        self.sz = 1.0
        self.px = 0.0
        self.py = 0.0
        self.pz = 0.0

        # View/camera parameters
        self.view_angle_x = 0.0
        self.view_angle_y = 0.0
        self.zoom = 1.0

        # Mouse tracking
        self.mouse_dragging = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.reset_button_rect = (20, 330, 140, 360)

        self.setup_gl()

    def setup_gl(self) -> None:
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glClearColor(0.1, 0.1, 0.15, 1.0)
        GLHelpers.setup_projection(self.width, self.height)

    def reset_all(self) -> None:
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0
        self.sx = 1.0
        self.sy = 1.0
        self.sz = 1.0
        self.px = 0.0
        self.py = 0.0
        self.pz = 0.0
        self.view_angle_x = 0.0
        self.view_angle_y = 0.0
        self.zoom = 1.0

    @staticmethod
    def is_point_in_rect(point: tuple, rect: tuple) -> bool:
        x, y = point
        x1, y1, x2, y2 = rect
        return x1 <= x <= x2 and y1 <= y <= y2

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                rot_step = 2.5 if (mods & pygame.KMOD_SHIFT) else 5.0
                scale_step = 0.02 if (mods & pygame.KMOD_SHIFT) else 0.05
                pivot_step = 0.05 if (mods & pygame.KMOD_SHIFT) else 0.1

                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
                if event.key == pygame.K_r:
                    self.reset_all()

                # Rotation controls
                if event.key == pygame.K_LEFT:
                    if mods & pygame.KMOD_SHIFT:
                        self.px -= pivot_step
                    else:
                        self.angle_x -= rot_step
                if event.key == pygame.K_RIGHT:
                    if mods & pygame.KMOD_SHIFT:
                        self.px += pivot_step
                    else:
                        self.angle_x += rot_step
                if event.key == pygame.K_UP:
                    if mods & pygame.KMOD_CTRL:
                        self.pz += pivot_step
                    elif mods & pygame.KMOD_SHIFT:
                        self.py += pivot_step
                    else:
                        self.angle_y += rot_step
                if event.key == pygame.K_DOWN:
                    if mods & pygame.KMOD_CTRL:
                        self.pz -= pivot_step
                    elif mods & pygame.KMOD_SHIFT:
                        self.py -= pivot_step
                    else:
                        self.angle_y -= rot_step
                if event.key == pygame.K_z:
                    if mods & pygame.KMOD_SHIFT:
                        self.angle_z += rot_step
                    else:
                        self.angle_z -= rot_step

                # Scaling controls
                if event.key == pygame.K_a:
                    self.sx = max(0.1, self.sx - scale_step)
                if event.key == pygame.K_d:
                    self.sx = min(3.0, self.sx + scale_step)
                if event.key == pygame.K_s:
                    self.sy = max(0.1, self.sy - scale_step)
                if event.key == pygame.K_w:
                    self.sy = min(3.0, self.sy + scale_step)
                if event.key == pygame.K_c:
                    self.sz = max(0.1, self.sz - scale_step)
                if event.key == pygame.K_e:
                    self.sz = min(3.0, self.sz + scale_step)

                # Zoom controls
                if event.key in (pygame.K_EQUALS, pygame.K_PLUS):
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
                elif event.button == 4:
                    self.zoom = min(3.0, self.zoom * 1.1)
                elif event.button == 5:
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

    def build_composite_matrix(self) -> np.ndarray:
        """Build M = T(p) * Rz * Ry * Rx * S * T(-p)."""
        scale_m = Matrix4.scaling(self.sx, self.sy, self.sz)
        rx = Matrix4.rotation_x(math.radians(self.angle_x))
        ry = Matrix4.rotation_y(math.radians(self.angle_y))
        rz = Matrix4.rotation_z(math.radians(self.angle_z))

        local = Matrix4.compose([rz, ry, rx, scale_m])
        return apply_transformation_with_pivot(local, (self.px, self.py, self.pz))

    def render(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -10)
        glScalef(self.zoom, self.zoom, self.zoom)
        glRotatef(self.view_angle_x, 1, 0, 0)
        glRotatef(self.view_angle_y, 0, 1, 0)
        glTranslatef(-1.5, -1.5, -1.5)

        GLHelpers.draw_grid(size=6.0, step=0.5)
        GLHelpers.draw_axes(length=1.0)

        # Original cube
        glPushMatrix()
        GLHelpers.draw_cube_wireframe(Cube.vertices(), color=(1.0, 1.0, 1.0), line_width=1.5)
        glPopMatrix()

        # Composite transformed cube
        glPushMatrix()
        matrix = self.build_composite_matrix()
        GLHelpers.apply_matrix_to_gl(matrix)
        GLHelpers.draw_cube_wireframe(Cube.vertices(), color=(0.0, 1.0, 1.0), line_width=2.0)
        glPopMatrix()

        # Pivot point marker
        glPushMatrix()
        glTranslatef(self.px, self.py, self.pz)
        glColor3f(1.0, 0.2, 0.2)
        glPointSize(6.0)
        glBegin(GL_POINTS)
        glVertex3f(0.0, 0.0, 0.0)
        glEnd()
        glPopMatrix()

        self.render_hud(matrix)

    def render_text_2d(self, text: str, x: float, y: float, color=(1.0, 1.0, 1.0)) -> None:
        glColor3f(*color)
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

    def render_hud(self, matrix: np.ndarray) -> None:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)

        # Reset button
        glColor3f(0.2, 0.5, 0.2)
        glBegin(GL_QUADS)
        glVertex2f(self.reset_button_rect[0], self.reset_button_rect[1])
        glVertex2f(self.reset_button_rect[2], self.reset_button_rect[1])
        glVertex2f(self.reset_button_rect[2], self.reset_button_rect[3])
        glVertex2f(self.reset_button_rect[0], self.reset_button_rect[3])
        glEnd()

        glColor3f(0.8, 1.0, 0.8)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.reset_button_rect[0], self.reset_button_rect[1])
        glVertex2f(self.reset_button_rect[2], self.reset_button_rect[1])
        glVertex2f(self.reset_button_rect[2], self.reset_button_rect[3])
        glVertex2f(self.reset_button_rect[0], self.reset_button_rect[3])
        glEnd()
        glLineWidth(1.0)

        hud_lines = [
            "3D Composite Transformation",
            "",
            f"Angles: X={self.angle_x:7.1f}  Y={self.angle_y:7.1f}  Z={self.angle_z:7.1f}",
            f"Scale : X={self.sx:7.2f}  Y={self.sy:7.2f}  Z={self.sz:7.2f}",
            f"Pivot : ({self.px:7.2f}, {self.py:7.2f}, {self.pz:7.2f})",
            f"Zoom  : {self.zoom:5.2f}x",
            "",
            "Order: T(p) * Rz * Ry * Rx * S * T(-p)",
            "Matrix:",
            GLHelpers.matrix_to_string(matrix, precision=2),
        ]

        y = 20
        for line in hud_lines:
            if not line:
                y += 16
                continue
            for subline in line.splitlines():
                self.render_text_2d(subline, 20, y, color=(1.0, 1.0, 1.0))
                y += 16

        # Right-side compact controls panel
        panel_lines = [
            "CONTROLS",
            "",
            "Mouse Drag: Rotate view",
            "Wheel / +/-: Zoom",
            "Left/Right: Rot X",
            "Up/Down: Rot Y",
            "Z/z: Rot Z +/-",
            "A/D: Scale X -/+",
            "S/W: Scale Y -/+",
            "C/E: Scale Z -/+",
            "Shift+Arrows: Pivot X/Y",
            "Ctrl+Up/Down: Pivot Z",
            "Shift: Fine step",
            "R: Reset   Q/ESC: Quit",
        ]

        box_w = 270
        box_h = len(panel_lines) * 14 + 10
        box_x = self.width - box_w - 10
        box_y = 10

        glColor4f(0.05, 0.15, 0.05, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(box_x, box_y)
        glVertex2f(box_x + box_w, box_y)
        glVertex2f(box_x + box_w, box_y + box_h)
        glVertex2f(box_x, box_y + box_h)
        glEnd()

        glColor3f(0.2, 1.0, 0.2)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(box_x, box_y)
        glVertex2f(box_x + box_w, box_y)
        glVertex2f(box_x + box_w, box_y + box_h)
        glVertex2f(box_x, box_y + box_h)
        glEnd()
        glLineWidth(1.0)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        y2 = box_y + 15
        for line in panel_lines:
            if line.strip():
                self.render_text_2d(line, box_x + 8, y2, color=(0.2, 1.0, 0.2))
            y2 += 14
        glDisable(GL_BLEND)

        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def run(self) -> None:
        clock = pygame.time.Clock()
        running = True
        while running:
            running = self.handle_events()
            self.render()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    app = CompositeTransformation3D()
    app.run()
