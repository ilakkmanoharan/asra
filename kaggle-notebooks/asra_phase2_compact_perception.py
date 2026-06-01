"""Standalone compact object perception for Kaggle my_agent (no asra-arc install)."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Tuple


def dominant_background(grid: List[List[int]]) -> int:
    counts: Counter[int] = Counter()
    for row in grid:
        counts.update(row)
    return counts.most_common(1)[0][0] if counts else 0


def connected_components(
    grid: List[List[int]], background: int, connectivity: int = 4
) -> List[Tuple[int, List[Tuple[int, int]]]]:
    h = len(grid)
    w = len(grid[0]) if h else 0
    visited = [[False] * w for _ in range(h)]
    components: List[Tuple[int, List[Tuple[int, int]]]] = []
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
            pixels: List[Tuple[int, int]] = []
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


def _bbox(pixels: List[Tuple[int, int]]) -> Tuple[int, int, int, int]:
    ys = [p[0] for p in pixels]
    xs = [p[1] for p in pixels]
    return min(ys), min(xs), max(ys), max(xs)


def _centroid(pixels: List[Tuple[int, int]]) -> Tuple[float, float]:
    n = len(pixels)
    if n == 0:
        return 0.0, 0.0
    return sum(p[0] for p in pixels) / n, sum(p[1] for p in pixels) / n


def compact_scene(grid: List[List[int]]) -> Dict[str, Any]:
    if not grid or not grid[0]:
        return {"grid_shape": [0, 0], "background_color": 0, "num_objects": 0, "objects": []}
    bg = dominant_background(grid)
    objects = []
    for idx, (color, pixels) in enumerate(connected_components(grid, bg)):
        if not pixels:
            continue
        bbox = _bbox(pixels)
        cy, cx = _centroid(pixels)
        objects.append(
            {
                "object_id": f"obj_{idx}",
                "color": int(color),
                "area": len(pixels),
                "bbox": list(bbox),
                "centroid": [cy, cx],
            }
        )
    return {
        "grid_shape": [len(grid), len(grid[0])],
        "background_color": int(bg),
        "num_objects": len(objects),
        "objects": objects,
    }


def object_delta(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "delta_num_objects": int(after.get("num_objects", 0)) - int(before.get("num_objects", 0)),
        "before_num_objects": int(before.get("num_objects", 0)),
        "after_num_objects": int(after.get("num_objects", 0)),
    }
