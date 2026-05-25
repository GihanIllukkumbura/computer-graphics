"""
Lecture 07: Scan-Line Polygon Filling (GUI)
===========================================

Interactive teaching tool for the scan-line polygon filling algorithm.
Follows the lecture notes and uses the example polygon:
    {(2,7), (4,12), (8,15), (16,9), (11,5), (8,7), (5,5)}

Controls:
    - Left Click: add a vertex (snapped to grid)
    - Right Click: close polygon
    - E: load lecture example polygon
    - F: compute fill (full)
    - S: toggle step mode
    - SPACE: advance one scanline step (step mode)
    - U: undo last vertex
    - C: clear
    - G: toggle grid
    - D: toggle debug panel
    - ESC: quit
"""

from dataclasses import dataclass
import math
import sys
import pygame

# ============================================================
# Configuration
# ============================================================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
COORD_SCALE = 20  # screen pixels per 1 logical unit
POINT_RADIUS = 5
BG_COLOR = (255, 255, 255)
GRID_COLOR = (235, 235, 235)
AXIS_COLOR = (190, 190, 190)
EDGE_COLOR = (30, 60, 140)
VERTEX_COLOR = (210, 40, 40)
FILL_COLOR = (80, 180, 120)
SCANLINE_COLOR = (255, 160, 0)
TEXT_COLOR = (20, 20, 20)
DEBUG_COLOR = (30, 30, 30)

LECTURE_EXAMPLE = [(2, 7), (4, 12), (8, 15), (16, 9), (11, 5), (8, 7), (5, 5)]


@dataclass
class Edge:
    y_max: int
    x: float
    inv_slope: float


@dataclass
class ScanStep:
    y: int
    spans: list
    intersections: list
    aet_snapshot: list


def cartesian_to_screen(cx, cy):
    """Convert Cartesian coords to screen coords (center origin)."""
    sx = WINDOW_WIDTH // 2 + int(round(cx * COORD_SCALE))
    sy = WINDOW_HEIGHT // 2 - int(round(cy * COORD_SCALE))
    return sx, sy


def screen_to_cartesian(sx, sy):
    """Convert screen coords to Cartesian coords with grid snapping."""
    cx = (sx - WINDOW_WIDTH // 2) / COORD_SCALE
    cy = (WINDOW_HEIGHT // 2 - sy) / COORD_SCALE
    return int(round(cx)), int(round(cy))


def draw_grid(surface, spacing=COORD_SCALE):
    """Draw a light Cartesian grid."""
    w, h = surface.get_size()
    cx, cy = w // 2, h // 2

    for x in range(cx % spacing, w, spacing):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, h), 1)
    for y in range(cy % spacing, h, spacing):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (w, y), 1)


def draw_axes(surface):
    """Draw x and y axes crossing at origin."""
    w, h = surface.get_size()
    cx, cy = w // 2, h // 2
    pygame.draw.line(surface, AXIS_COLOR, (0, cy), (w, cy), 2)
    pygame.draw.line(surface, AXIS_COLOR, (cx, 0), (cx, h), 2)


def draw_vertices(surface, font, points):
    """Draw polygon vertices and labels."""
    for i, (x, y) in enumerate(points, start=1):
        sx, sy = cartesian_to_screen(x, y)
        pygame.draw.circle(surface, VERTEX_COLOR, (sx, sy), POINT_RADIUS)
        label = font.render(f"V{i}({x},{y})", True, TEXT_COLOR)
        surface.blit(label, (sx + 8, sy - 18))


def draw_polygon_edges(surface, points, closed):
    """Draw polygon edges."""
    if len(points) < 2:
        return
    screen_points = [cartesian_to_screen(x, y) for x, y in points]
    if closed:
        pygame.draw.polygon(surface, EDGE_COLOR, screen_points, 2)
    else:
        pygame.draw.lines(surface, EDGE_COLOR, False, screen_points, 2)


def draw_span(surface, y, x_start, x_end, color):
    """Draw a filled span at scanline y from x_start to x_end (inclusive)."""
    if x_start > x_end:
        return
    sx, sy = cartesian_to_screen(x_start, y)
    width = (x_end - x_start + 1) * COORD_SCALE
    rect = pygame.Rect(sx - COORD_SCALE // 2, sy - COORD_SCALE // 2, width, COORD_SCALE)
    pygame.draw.rect(surface, color, rect)


def draw_scanline(surface, y):
    """Highlight the current scanline."""
    _, sy = cartesian_to_screen(0, y)
    pygame.draw.line(surface, SCANLINE_COLOR, (0, sy), (WINDOW_WIDTH, sy), 1)


def normalize_polygon(points):
    """Remove duplicate last point and ensure integer vertices."""
    if len(points) >= 2 and points[0] == points[-1]:
        points = points[:-1]
    return [(int(round(x)), int(round(y))) for x, y in points]


def build_edge_table(points):
    """
    Build edge table (ET) using the lecture rule:
    exclude upper endpoints by setting y_max = upper_y - 1
    to avoid double-counted vertex intersections.
    """
    points = normalize_polygon(points)
    if len(points) < 3:
        return {}, None, None

    et = {}
    min_y = None
    max_y = None
    n = len(points)

    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]

        if y1 == y2:
            continue  # skip horizontal edges

        if y1 < y2:
            y_min = y1
            y_max = y2 - 1
            x_at_y_min = x1
            inv_slope = (x2 - x1) / (y2 - y1)
        else:
            y_min = y2
            y_max = y1 - 1
            x_at_y_min = x2
            inv_slope = (x1 - x2) / (y1 - y2)

        if y_max < y_min:
            continue

        et.setdefault(y_min, []).append(Edge(y_max=y_max, x=float(x_at_y_min), inv_slope=inv_slope))
        min_y = y_min if min_y is None else min(min_y, y_min)
        max_y = y_max if max_y is None else max(max_y, y_max)

    for y in et:
        et[y].sort(key=lambda e: (e.x, e.inv_slope))

    return et, min_y, max_y


def build_scan_steps(points):
    """Compute scanline steps (ET, AET, intersections, spans)."""
    edge_table, min_y, max_y = build_edge_table(points)
    if min_y is None or max_y is None:
        return [], edge_table, min_y, max_y

    aet = []
    steps = []

    for y in range(min_y, max_y + 1):
        if y in edge_table:
            aet.extend(edge_table[y])

        # Remove edges where scanline has passed the edge's y_max
        aet = [e for e in aet if y <= e.y_max]
        aet.sort(key=lambda e: (e.x, e.inv_slope))

        intersections = [e.x for e in aet]
        spans = []
        for i in range(0, len(intersections) - 1, 2):
            x_start = math.ceil(intersections[i])
            x_end = math.floor(intersections[i + 1])
            if x_start <= x_end:
                spans.append((x_start, x_end))

        steps.append(
            ScanStep(
                y=y,
                spans=spans,
                intersections=intersections[:],
                aet_snapshot=[(e.x, e.y_max, e.inv_slope) for e in aet],
            )
        )

        # Update x for next scanline
        for e in aet:
            e.x += e.inv_slope

    return steps, edge_table, min_y, max_y


def render_debug_panel(surface, font, steps, edge_table, step_index):
    """Render debug information for the current scanline."""
    x0 = WINDOW_WIDTH - 360
    y0 = 20
    lines = [
        "Scan-Line Fill Debug",
        "---------------------",
    ]

    if not steps:
        lines.append("No fill data")
    else:
        step = steps[step_index]
        lines.append(f"Scanline y = {step.y}")
        lines.append(f"Intersections: {', '.join(f'{x:.2f}' for x in step.intersections) or 'none'}")
        lines.append(f"Spans: {', '.join(f'[{a},{b}]' for a, b in step.spans) or 'none'}")
        lines.append("AET (x, y_max, 1/m):")
        if step.aet_snapshot:
            for x, y_max, inv_m in step.aet_snapshot[:6]:
                lines.append(f"  ({x:.2f}, {y_max}, {inv_m:.3f})")
            if len(step.aet_snapshot) > 6:
                lines.append(f"  ... +{len(step.aet_snapshot) - 6} more")
        else:
            lines.append("  empty")

    lines.append("")
    lines.append("ET entries (y_min -> count):")
    for y_min in sorted(edge_table.keys())[:8]:
        lines.append(f"  y={y_min}: {len(edge_table[y_min])} edges")
    if len(edge_table.keys()) > 8:
        lines.append("  ...")

    for i, text in enumerate(lines):
        surface.blit(font.render(text, True, DEBUG_COLOR), (x0, y0 + i * 18))


def render_instructions(surface, font, step_mode, filled):
    """Render on-screen controls and steps summary."""
    lines = [
        "Controls: LMB add | RMB close | E example | F fill | S step | SPACE next | U undo",
        "          C clear | G grid | D debug | ESC quit",
        f"Mode: {'STEP' if step_mode else 'FULL'} | Filled: {'YES' if filled else 'NO'}",
        "Algorithm steps: build ET -> move edges to AET -> sort -> pair intersections -> fill spans -> update x",
    ]
    for i, text in enumerate(lines):
        surface.blit(font.render(text, True, TEXT_COLOR), (10, 10 + i * 20))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Lecture 07: Scan-Line Polygon Fill")
    font = pygame.font.SysFont("Consolas", 16)
    title_font = pygame.font.SysFont("Consolas", 20)
    clock = pygame.time.Clock()

    polygon_points = []
    polygon_closed = False
    show_grid = True
    show_debug = False
    step_mode = False

    steps = []
    edge_table = {}
    step_index = 0

    def clear_fill():
        nonlocal steps, edge_table, step_index
        steps = []
        edge_table = {}
        step_index = 0

    def compute_fill():
        nonlocal steps, edge_table, step_index
        steps, edge_table, _, _ = build_scan_steps(polygon_points)
        step_index = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    polygon_points = []
                    polygon_closed = False
                    clear_fill()
                elif event.key == pygame.K_g:
                    show_grid = not show_grid
                elif event.key == pygame.K_d:
                    show_debug = not show_debug
                elif event.key == pygame.K_u and polygon_points:
                    polygon_points.pop()
                    polygon_closed = False
                    clear_fill()
                elif event.key == pygame.K_e:
                    polygon_points = LECTURE_EXAMPLE[:]
                    polygon_closed = True
                    clear_fill()
                elif event.key == pygame.K_s:
                    step_mode = not step_mode
                elif event.key == pygame.K_f:
                    if polygon_closed and len(polygon_points) >= 3:
                        compute_fill()
                elif event.key == pygame.K_SPACE:
                    if step_mode and steps:
                        step_index = min(step_index + 1, len(steps) - 1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not polygon_closed:
                    cx, cy = screen_to_cartesian(*event.pos)
                    polygon_points.append((cx, cy))
                    clear_fill()
                elif event.button == 3 and len(polygon_points) >= 3:
                    polygon_closed = True
                    clear_fill()

        screen.fill(BG_COLOR)
        if show_grid:
            draw_grid(screen)
        draw_axes(screen)

        # Filled spans
        if steps:
            if step_mode:
                max_step = step_index
            else:
                max_step = len(steps) - 1
            for step in steps[: max_step + 1]:
                for x_start, x_end in step.spans:
                    draw_span(screen, step.y, x_start, x_end, FILL_COLOR)

            if step_mode and steps:
                draw_scanline(screen, steps[step_index].y)

        # Polygon on top
        draw_polygon_edges(screen, polygon_points, polygon_closed)
        draw_vertices(screen, font, polygon_points)

        title = title_font.render("Scan-Line Polygon Filling", True, TEXT_COLOR)
        screen.blit(title, (10, WINDOW_HEIGHT - 32))

        render_instructions(screen, font, step_mode, bool(steps))

        if show_debug and steps:
            render_debug_panel(screen, font, steps, edge_table, step_index)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
