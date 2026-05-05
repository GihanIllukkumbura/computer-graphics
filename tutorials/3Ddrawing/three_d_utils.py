"""
Shared 3D transformation utilities for interactive OpenGL tutorials.

Includes matrix operations, cube mesh generation, and OpenGL rendering helpers.
"""

import numpy as np
from typing import Tuple, List
from OpenGL.GL import *
from OpenGL.GLU import gluLookAt, gluPerspective


class Matrix4:
    """4x4 homogeneous transformation matrix utilities."""

    @staticmethod
    def identity() -> np.ndarray:
        """Return 4x4 identity matrix."""
        return np.eye(4, dtype=np.float32)

    @staticmethod
    def translation(tx: float, ty: float, tz: float) -> np.ndarray:
        """Return 4x4 translation matrix."""
        M = Matrix4.identity()
        M[0, 3] = tx
        M[1, 3] = ty
        M[2, 3] = tz
        return M

    @staticmethod
    def scaling(sx: float, sy: float, sz: float) -> np.ndarray:
        """Return 4x4 scaling matrix."""
        M = Matrix4.identity()
        M[0, 0] = sx
        M[1, 1] = sy
        M[2, 2] = sz
        return M

    @staticmethod
    def rotation_x(angle_rad: float) -> np.ndarray:
        """Return 4x4 rotation matrix around X-axis (angle in radians)."""
        c = np.cos(angle_rad)
        s = np.sin(angle_rad)
        M = Matrix4.identity()
        M[1, 1] = c
        M[1, 2] = -s
        M[2, 1] = s
        M[2, 2] = c
        return M

    @staticmethod
    def rotation_y(angle_rad: float) -> np.ndarray:
        """Return 4x4 rotation matrix around Y-axis (angle in radians)."""
        c = np.cos(angle_rad)
        s = np.sin(angle_rad)
        M = Matrix4.identity()
        M[0, 0] = c
        M[0, 2] = s
        M[2, 0] = -s
        M[2, 2] = c
        return M

    @staticmethod
    def rotation_z(angle_rad: float) -> np.ndarray:
        """Return 4x4 rotation matrix around Z-axis (angle in radians)."""
        c = np.cos(angle_rad)
        s = np.sin(angle_rad)
        M = Matrix4.identity()
        M[0, 0] = c
        M[0, 1] = -s
        M[1, 0] = s
        M[1, 1] = c
        return M

    @staticmethod
    def reflection_xy() -> np.ndarray:
        """Return 4x4 reflection matrix across XY plane (z -> -z)."""
        M = Matrix4.identity()
        M[2, 2] = -1
        return M

    @staticmethod
    def reflection_yz() -> np.ndarray:
        """Return 4x4 reflection matrix across YZ plane (x -> -x)."""
        M = Matrix4.identity()
        M[0, 0] = -1
        return M

    @staticmethod
    def reflection_xz() -> np.ndarray:
        """Return 4x4 reflection matrix across XZ plane (y -> -y)."""
        M = Matrix4.identity()
        M[1, 1] = -1
        return M

    @staticmethod
    def reflection_origin() -> np.ndarray:
        """Return 4x4 reflection matrix through origin (inversion)."""
        M = Matrix4.identity()
        M[0, 0] = -1
        M[1, 1] = -1
        M[2, 2] = -1
        return M

    @staticmethod
    def shear_xy(shx: float, shy: float) -> np.ndarray:
        """Return 4x4 shearing matrix in XY plane (shear X by Y and vice versa)."""
        M = Matrix4.identity()
        M[0, 1] = shx
        M[1, 0] = shy
        return M

    @staticmethod
    def shear_yz(shy: float, shz: float) -> np.ndarray:
        """Return 4x4 shearing matrix in YZ plane."""
        M = Matrix4.identity()
        M[1, 2] = shy
        M[2, 1] = shz
        return M

    @staticmethod
    def shear_xz(shx: float, shz: float) -> np.ndarray:
        """Return 4x4 shearing matrix in XZ plane."""
        M = Matrix4.identity()
        M[0, 2] = shx
        M[2, 0] = shz
        return M

    @staticmethod
    def compose(matrices: List[np.ndarray]) -> np.ndarray:
        """Compose multiple transformation matrices (right-to-left order)."""
        result = Matrix4.identity()
        for M in matrices:
            result = result @ M
        return result

    @staticmethod
    def apply_to_point(M: np.ndarray, point: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Apply 4x4 matrix to 3D point (converts to homogeneous coords, applies, projects back)."""
        p = np.array([point[0], point[1], point[2], 1.0], dtype=np.float32)
        p_transformed = M @ p
        if p_transformed[3] != 0:
            return (p_transformed[0] / p_transformed[3], p_transformed[1] / p_transformed[3], p_transformed[2] / p_transformed[3])
        return (p_transformed[0], p_transformed[1], p_transformed[2])


class Cube:
    """Unit cube geometry and rendering."""

    @staticmethod
    def vertices() -> np.ndarray:
        """Return 8 vertices of a cube centered at origin, ranging from -0.5 to 0.5."""
        return np.array([
            [-0.5, -0.5, -0.5],
            [ 0.5, -0.5, -0.5],
            [ 0.5,  0.5, -0.5],
            [-0.5,  0.5, -0.5],
            [-0.5, -0.5,  0.5],
            [ 0.5, -0.5,  0.5],
            [ 0.5,  0.5,  0.5],
            [-0.5,  0.5,  0.5],
        ], dtype=np.float32)

    @staticmethod
    def edges() -> List[Tuple[int, int]]:
        """Return list of edge indices (vertex pairs) for the cube."""
        return [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom face
            (4, 5), (5, 6), (6, 7), (7, 4),  # Top face
            (0, 4), (1, 5), (2, 6), (3, 7),  # Vertical edges
        ]

    @staticmethod
    def faces() -> List[Tuple[int, int, int, int]]:
        """Return list of face indices (quads) for the cube."""
        return [
            (0, 1, 2, 3),  # Bottom
            (4, 7, 6, 5),  # Top
            (0, 3, 7, 4),  # Left
            (1, 5, 6, 2),  # Right
            (0, 4, 5, 1),  # Front
            (2, 6, 7, 3),  # Back
        ]


class GLHelpers:
    """OpenGL rendering utilities."""

    @staticmethod
    def setup_projection(width: int, height: int, fov: float = 45.0, near: float = 0.1, far: float = 100.0) -> None:
        """Setup perspective projection."""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / height if height > 0 else 1.0
        gluPerspective(fov, aspect, near, far)
        glMatrixMode(GL_MODELVIEW)

    @staticmethod
    def setup_view(eye_x: float, eye_y: float, eye_z: float, center_x: float = 0.0, center_y: float = 0.0, center_z: float = 0.0) -> None:
        """Setup camera view."""
        glLoadIdentity()
        gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 1, 0)

    @staticmethod
    def draw_cube_wireframe(vertices: np.ndarray, color: Tuple[float, float, float] = (1.0, 1.0, 1.0), line_width: float = 1.0) -> None:
        """Draw cube wireframe from vertices."""
        glColor3f(*color)
        glLineWidth(line_width)
        glBegin(GL_LINES)
        for edge in Cube.edges():
            for idx in edge:
                v = vertices[idx]
                glVertex3f(v[0], v[1], v[2])
        glEnd()
        glLineWidth(1.0)

    @staticmethod
    def draw_axes(length: float = 1.0, line_width: float = 2.0) -> None:
        """Draw RGB axes at origin."""
        glLineWidth(line_width)
        glBegin(GL_LINES)
        # X-axis (red)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(length, 0.0, 0.0)
        # Y-axis (green)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, length, 0.0)
        # Z-axis (blue)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, length)
        glEnd()
        glLineWidth(1.0)

    @staticmethod
    def draw_grid(size: float = 5.0, step: float = 0.5, color: Tuple[float, float, float] = (0.3, 0.3, 0.3)) -> None:
        """Draw XZ grid at y=0 (horizontal plane)."""
        glColor3f(*color)
        glLineWidth(0.5)
        glBegin(GL_LINES)
        half = size / 2
        while True:
            x = -half
            while x <= half:
                glVertex3f(x, 0.0, -half)
                glVertex3f(x, 0.0, half)
                x += step
                if x > half:
                    break
            break
        x = -half
        while x <= half:
            glVertex3f(-half, 0.0, x)
            glVertex3f(half, 0.0, x)
            x += step
        glEnd()
        glLineWidth(1.0)

    @staticmethod
    def apply_matrix_to_gl(matrix: np.ndarray) -> None:
        """Apply 4x4 matrix to OpenGL modelview."""
        glMultMatrixf(matrix.T.flatten())

    @staticmethod
    def matrix_to_string(matrix: np.ndarray, precision: int = 2) -> str:
        """Format 4x4 matrix as readable string for HUD display."""
        lines = []
        fmt = f"{{:7.{precision}f}}"
        for i in range(4):
            row_str = "  ".join(fmt.format(matrix[i, j]) for j in range(4))
            lines.append(row_str)
        return "\n".join(lines)

    @staticmethod
    def render_text_box(x: int, y: int, text_lines: List[str], bg_color: Tuple[float, float, float] = (0.1, 0.1, 0.1), text_color: Tuple[float, float, float] = (0.2, 1.0, 0.2), line_height: int = 16, box_width: int = 250) -> None:
        """Render a text box with background at (x, y) in screen coordinates.
        
        This uses simple OpenGL rendering of colored rectangles for the background and assumes text will be rendered separately if needed.
        """
        # Draw semi-transparent background box
        box_height = len(text_lines) * line_height + 10
        glColor4f(*bg_color, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + box_width, y)
        glVertex2f(x + box_width, y + box_height)
        glVertex2f(x, y + box_height)
        glEnd()
        
        # Draw border
        glColor3f(*text_color)
        glLineWidth(1.5)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + box_width, y)
        glVertex2f(x + box_width, y + box_height)
        glVertex2f(x, y + box_height)
        glEnd()
        glLineWidth(1.0)


def apply_transformation_with_pivot(transform_matrix: np.ndarray, pivot: Tuple[float, float, float]) -> np.ndarray:
    """
    Compose transformation around pivot point: T(pivot) * M * T(-pivot)
    
    Args:
        transform_matrix: The transformation to apply (rotation, scale, etc.)
        pivot: The pivot point (px, py, pz)
    
    Returns:
        Composed 4x4 matrix
    """
    T_pivot = Matrix4.translation(pivot[0], pivot[1], pivot[2])
    T_neg_pivot = Matrix4.translation(-pivot[0], -pivot[1], -pivot[2])
    return Matrix4.compose([T_pivot, transform_matrix, T_neg_pivot])
