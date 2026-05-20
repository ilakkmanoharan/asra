from __future__ import annotations


def diff_grid(prev_grid: list[list[int]], next_grid: list[list[int]]) -> dict:
    if len(prev_grid) != len(next_grid) or (prev_grid and next_grid and len(prev_grid[0]) != len(next_grid[0])):
        raise ValueError("Grid shapes must match for differencing")
    changed_cells = []
    prev_colors = set()
    next_colors = set()
    total = 0
    for y, (prev_row, next_row) in enumerate(zip(prev_grid, next_grid)):
        if len(prev_row) != len(next_row):
            raise ValueError("Grid shapes must match for differencing")
        for x, (before, after) in enumerate(zip(prev_row, next_row)):
            total += 1
            prev_colors.add(before)
            next_colors.add(after)
            if before != after:
                changed_cells.append({"x": x, "y": y, "from": before, "to": after})
    num_changed = len(changed_cells)
    change_ratio = num_changed / total if total else 0.0
    return {
        "changed_cells": changed_cells,
        "num_changed_cells": num_changed,
        "change_ratio": change_ratio,
        "added_colors": sorted(next_colors - prev_colors),
        "removed_colors": sorted(prev_colors - next_colors),
        "unchanged_ratio": 1.0 - change_ratio,
    }
