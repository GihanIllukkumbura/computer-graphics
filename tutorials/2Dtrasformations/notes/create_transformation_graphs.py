"""
Create high-quality Cartesian plane graphs for transformation notes.

Outputs PNG files into tutorials/2Dtrasformations/notes/figures.
"""

from __future__ import annotations

from pathlib import Path
import math

import matplotlib.pyplot as plt
import numpy as np


NOTES_DIR = Path(__file__).resolve().parent
FIGURES_DIR = NOTES_DIR / "figures"

BASE_SHAPE = np.array(
    [
        [-4.0, -2.0],
        [2.0, -2.0],
        [3.0, 1.0],
        [-1.0, 3.0],
    ]
)


def setup_axes(title: str) -> tuple[plt.Figure, plt.Axes]:
    """Create styled Cartesian plane axes."""
    fig, ax = plt.subplots(figsize=(8.0, 6.0), dpi=220)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlim(-12, 12)
    ax.set_ylim(-10, 10)
    ax.set_aspect("equal", adjustable="box")

    ax.grid(True, linestyle="--", linewidth=0.6, color="#d0d0d0", alpha=0.9)
    ax.axhline(0.0, color="#666666", linewidth=1.2)
    ax.axvline(0.0, color="#666666", linewidth=1.2)

    ax.set_xlabel("x")
    ax.set_ylabel("y")

    ax.set_xticks(np.arange(-12, 13, 2))
    ax.set_yticks(np.arange(-10, 11, 2))

    return fig, ax


def draw_shape(ax: plt.Axes, points: np.ndarray, color: str, label: str, line_style: str = "-") -> None:
    """Draw polygon and vertices."""
    closed = np.vstack([points, points[0]])
    ax.plot(closed[:, 0], closed[:, 1], line_style, color=color, linewidth=2.4, label=label)
    ax.scatter(points[:, 0], points[:, 1], color=color, s=28, zorder=5)


def draw_mapping(ax: plt.Axes, src: np.ndarray, dst: np.ndarray) -> None:
    """Draw vertex mapping segments between original and transformed points."""
    for a, b in zip(src, dst):
        ax.plot([a[0], b[0]], [a[1], b[1]], color="#9a9a9a", linewidth=1.0, alpha=0.85)


def save_figure(fig: plt.Figure, filename: str) -> None:
    """Save figure with consistent quality."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / filename, dpi=220)
    plt.close(fig)


def translation_graph() -> None:
    tx, ty = 4.0, 3.0
    transformed = BASE_SHAPE + np.array([tx, ty])

    fig, ax = setup_axes("2D Translation on Cartesian Plane")
    draw_mapping(ax, BASE_SHAPE, transformed)
    draw_shape(ax, BASE_SHAPE, "#1f5fd5", "Original")
    draw_shape(ax, transformed, "#d23838", "Translated")

    ax.legend(loc="upper left")
    ax.text(
        -11.5,
        -9.1,
        f"x' = x + {tx:.1f},  y' = y + {ty:.1f}",
        fontsize=10,
        bbox={"facecolor": "white", "edgecolor": "#888", "pad": 4},
    )

    save_figure(fig, "01_translation_cartesian.png")


def scaling_graph() -> None:
    sx, sy = 1.6, 0.7
    pivot = np.array([1.5, 1.0])
    transformed = pivot + np.column_stack((sx * (BASE_SHAPE[:, 0] - pivot[0]), sy * (BASE_SHAPE[:, 1] - pivot[1])))

    fig, ax = setup_axes("2D Scaling Around Pivot")
    draw_mapping(ax, BASE_SHAPE, transformed)
    draw_shape(ax, BASE_SHAPE, "#1f5fd5", "Original")
    draw_shape(ax, transformed, "#d23838", "Scaled")

    ax.scatter([pivot[0]], [pivot[1]], color="#0a8f4b", s=55, label="Pivot")
    ax.text(pivot[0] + 0.3, pivot[1] + 0.4, f"P({pivot[0]:.1f}, {pivot[1]:.1f})", fontsize=9)

    ax.legend(loc="upper left")
    ax.text(
        -11.5,
        -9.1,
        f"sx={sx:.2f}, sy={sy:.2f};  x' = px + sx(x-px), y' = py + sy(y-py)",
        fontsize=9,
        bbox={"facecolor": "white", "edgecolor": "#888", "pad": 4},
    )

    save_figure(fig, "02_scaling_cartesian.png")


def rotation_graph() -> None:
    angle_deg = 35.0
    theta = math.radians(angle_deg)
    c = math.cos(theta)
    s = math.sin(theta)
    pivot = np.array([1.5, 1.0])

    rel = BASE_SHAPE - pivot
    transformed = np.column_stack((c * rel[:, 0] - s * rel[:, 1], s * rel[:, 0] + c * rel[:, 1])) + pivot

    fig, ax = setup_axes("2D Rotation Around Pivot")
    draw_mapping(ax, BASE_SHAPE, transformed)
    draw_shape(ax, BASE_SHAPE, "#1f5fd5", "Original")
    draw_shape(ax, transformed, "#d23838", "Rotated")

    ax.scatter([pivot[0]], [pivot[1]], color="#0a8f4b", s=55, label="Pivot")
    ax.legend(loc="upper left")

    ax.text(
        -11.5,
        -9.1,
        f"theta={angle_deg:.1f} deg;  R(theta) applied after translate to pivot",
        fontsize=9,
        bbox={"facecolor": "white", "edgecolor": "#888", "pad": 4},
    )

    save_figure(fig, "03_rotation_cartesian.png")


def reflection_graph() -> None:
    transformed = np.column_stack((BASE_SHAPE[:, 1], BASE_SHAPE[:, 0]))

    fig, ax = setup_axes("2D Reflection About Line y = x")
    ax.plot([-12, 12], [-12, 12], color="#0a8f4b", linewidth=2.0, linestyle="--", label="Mirror line y=x")

    draw_mapping(ax, BASE_SHAPE, transformed)
    draw_shape(ax, BASE_SHAPE, "#1f5fd5", "Original")
    draw_shape(ax, transformed, "#d23838", "Reflected")

    ax.legend(loc="upper left")
    ax.text(
        -11.5,
        -9.1,
        "Reflection y=x: x' = y, y' = x",
        fontsize=10,
        bbox={"facecolor": "white", "edgecolor": "#888", "pad": 4},
    )

    save_figure(fig, "04_reflection_cartesian.png")


def shearing_graph() -> None:
    shx, shy = 0.6, 0.0
    transformed = np.column_stack((BASE_SHAPE[:, 0] + shx * BASE_SHAPE[:, 1], BASE_SHAPE[:, 1] + shy * BASE_SHAPE[:, 0]))

    fig, ax = setup_axes("2D Shearing on Cartesian Plane")
    draw_mapping(ax, BASE_SHAPE, transformed)
    draw_shape(ax, BASE_SHAPE, "#1f5fd5", "Original")
    draw_shape(ax, transformed, "#d23838", "Sheared")

    ax.legend(loc="upper left")
    ax.text(
        -11.5,
        -9.1,
        f"X-shear example: shx={shx:.2f}; x' = x + shx*y",
        fontsize=10,
        bbox={"facecolor": "white", "edgecolor": "#888", "pad": 4},
    )

    save_figure(fig, "05_shearing_cartesian.png")


def translation_matrix(tx: float, ty: float) -> np.ndarray:
    """Build homogeneous translation matrix."""
    return np.array(
        [
            [1.0, 0.0, tx],
            [0.0, 1.0, ty],
            [0.0, 0.0, 1.0],
        ]
    )


def scaling_matrix(sx: float, sy: float) -> np.ndarray:
    """Build homogeneous scaling matrix."""
    return np.array(
        [
            [sx, 0.0, 0.0],
            [0.0, sy, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


def rotation_matrix(theta_deg: float) -> np.ndarray:
    """Build homogeneous rotation matrix."""
    t = math.radians(theta_deg)
    c = math.cos(t)
    s = math.sin(t)
    return np.array(
        [
            [c, -s, 0.0],
            [s, c, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


def shear_matrix(shx: float, shy: float) -> np.ndarray:
    """Build homogeneous shear matrix."""
    return np.array(
        [
            [1.0, shx, 0.0],
            [shy, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


def reflection_matrix_x() -> np.ndarray:
    """Build reflection matrix about local x-axis."""
    return np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


def apply_homogeneous(points: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Apply homogeneous matrix to array of points."""
    h = np.column_stack((points, np.ones(points.shape[0])))
    out = (matrix @ h.T).T
    out[:, 0] /= out[:, 2]
    out[:, 1] /= out[:, 2]
    return out[:, :2]


def composition_graph() -> None:
    tx, ty = 3.0, -1.0
    px, py = 1.5, 1.0
    angle = 30.0
    sx, sy = 1.4, 0.8
    shx, shy = 0.35, -0.20

    local = rotation_matrix(angle) @ shear_matrix(shx, shy) @ scaling_matrix(sx, sy) @ reflection_matrix_x()
    total = translation_matrix(tx, ty) @ translation_matrix(px, py) @ local @ translation_matrix(-px, -py)
    transformed = apply_homogeneous(BASE_SHAPE, total)

    fig, ax = setup_axes("Composed Transformations About Non-Origin Pivot")
    draw_mapping(ax, BASE_SHAPE, transformed)
    draw_shape(ax, BASE_SHAPE, "#1f5fd5", "Original")
    draw_shape(ax, transformed, "#d23838", "Composed result")

    ax.scatter([px], [py], color="#0a8f4b", s=55, label="Pivot")
    ax.legend(loc="upper left")

    ax.text(
        -11.5,
        -9.1,
        "M_total = T(tx,ty) * T(px,py) * M_local * T(-px,-py)",
        fontsize=8.8,
        bbox={"facecolor": "white", "edgecolor": "#888", "pad": 4},
    )

    save_figure(fig, "06_composition_cartesian.png")


def main() -> None:
    """Generate all graph files."""
    translation_graph()
    scaling_graph()
    rotation_graph()
    reflection_graph()
    shearing_graph()
    composition_graph()
    print("Transformation graph generation complete.")


if __name__ == "__main__":
    main()
