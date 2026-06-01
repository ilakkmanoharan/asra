from __future__ import annotations

from collections import Counter

from asra.perception.schemas import GridObject, ObjectScene


def _dominant_background(grid: list[list[int]]) -> int:
    counts: Counter[int] = Counter()
    for row in grid:
        counts.update(row)
    if not counts:
        return 0
    return counts.most_common(1)[0][0]


def _connected_components(
    grid: list[list[int]],
    background: int,
    connectivity: int = 4,
) -> list[tuple[int, list[tuple[int, int]]]]:
    h = len(grid)
    w = len(grid[0]) if h else 0
    visited = [[False] * w for _ in range(h)]
    components: list[tuple[int, list[tuple[int, int]]]] = []
    neighbors = (
        [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if connectivity == 4
        else [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    )

    for y in range(h):
        for x in range(w):
            color = grid[y][x]
            if color == background or visited[y][x]:
                continue
            stack = [(y, x)]
            visited[y][x] = True
            pixels: list[tuple[int, int]] = []
            while stack:
                cy, cx = stack.pop()
                pixels.append((cy, cx))
                for dy, dx in neighbors:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and not visited[ny][nx] and grid[ny][nx] == color:
                        visited[ny][nx] = True
                        stack.append((ny, nx))
            components.append((color, pixels))
    return components


def _bbox(pixels: list[tuple[int, int]]) -> tuple[int, int, int, int]:
    ys = [p[0] for p in pixels]
    xs = [p[1] for p in pixels]
    return min(ys), min(xs), max(ys), max(xs)


def _centroid(pixels: list[tuple[int, int]]) -> tuple[float, float]:
    n = len(pixels)
    if n == 0:
        return 0.0, 0.0
    sy = sum(p[0] for p in pixels)
    sx = sum(p[1] for p in pixels)
    return sy / n, sx / n


def compute_shape_hash(pixels: list[tuple[int, int]], color: int) -> str:
    from asra.perception.shapes import normalized_shape_signature

    return normalized_shape_signature(pixels, color)


class ObjectExtractor:
    """Segment integer grids into connected components (Phase 2 baseline)."""

    def __init__(self, min_area: int = 1, connectivity: int = 4, background_color: int | None = None) -> None:
        self.min_area = min_area
        self.connectivity = connectivity
        self.background_color = background_color

    def extract(self, grid: list[list[int]]) -> ObjectScene:
        if not grid or not grid[0]:
            return ObjectScene(grid_shape=(0, 0), background_color=0)
        h, w = len(grid), len(grid[0])
        bg = self.background_color if self.background_color is not None else _dominant_background(grid)
        components = _connected_components(grid, bg, self.connectivity)
        objects: list[GridObject] = []
        for idx, (color, pixels) in enumerate(components):
            if len(pixels) < self.min_area:
                continue
            bbox = _bbox(pixels)
            centroid = _centroid(pixels)
            shape_hash = compute_shape_hash(pixels, color)
            objects.append(
                GridObject(
                    object_id=f"obj_{idx}",
                    color=color,
                    pixels=tuple(pixels),
                    bbox=bbox,
                    area=len(pixels),
                    shape_hash=shape_hash,
                    centroid=centroid,
                )
            )
        return ObjectScene(
            grid_shape=(h, w),
            background_color=bg,
            objects=objects,
        )
