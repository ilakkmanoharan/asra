"""Color grid rendering for ARC-style replay (Phase 1 Priority 1)."""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

# ARC-like palette for indices 0–15
ARC_PALETTE = [
    "#000000", "#0074D9", "#FF4136", "#2ECC40", "#FFDC00", "#AAAAAA",
    "#F012BE", "#FF851B", "#7FDBFF", "#870C25", "#5C4B1F", "#2E8B57",
    "#FF6F61", "#7B3F98", "#00CED1", "#F5F5DC",
]
ARC_CMAP = ListedColormap(ARC_PALETTE[:16])


def grid_to_array(grid: list[list[int]]) -> np.ndarray:
    return np.array(grid, dtype=int)


def render_grid_figure(
    grid: list[list[int]],
    *,
    title: str = "",
    highlight: list[dict[str, Any]] | None = None,
    highlight_color: str = "#FF00FF",
) -> plt.Figure:
    arr = grid_to_array(grid)
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.imshow(arr, cmap=ARC_CMAP, vmin=0, vmax=15, interpolation="nearest")
    ax.set_title(title, fontsize=10)
    ax.set_xticks(range(arr.shape[1]))
    ax.set_yticks(range(arr.shape[0]))
    ax.tick_params(labelsize=7)
    if highlight:
        for cell in highlight:
            x, y = cell["x"], cell["y"]
            rect = plt.Rectangle((x - 0.5, y - 0.5), 1, 1, fill=False, edgecolor=highlight_color, linewidth=2)
            ax.add_patch(rect)
    fig.tight_layout()
    return fig


def render_diff_figure(grid: list[list[int]], changed_cells: list[dict[str, Any]], *, title: str = "Diff") -> plt.Figure:
    return render_grid_figure(grid, title=title, highlight=changed_cells, highlight_color="#FFD700")


def render_side_by_side(
    state_grid: list[list[int]],
    next_grid: list[list[int]],
    changed_cells: list[dict[str, Any]],
    *,
    action_name: str,
) -> plt.Figure:
    fig, axes = plt.subplots(1, 3, figsize=(9, 3))
    for ax, data, t in zip(
        axes,
        [state_grid, next_grid, state_grid],
        ["Before", f"After ({action_name})", "Changed cells"],
    ):
        arr = grid_to_array(data)
        ax.imshow(arr, cmap=ARC_CMAP, vmin=0, vmax=15, interpolation="nearest")
        ax.set_title(t, fontsize=9)
        if ax == axes[2]:
            for cell in changed_cells:
                x, y = cell["x"], cell["y"]
                rect = plt.Rectangle((x - 0.5, y - 0.5), 1, 1, fill=False, edgecolor="#FFD700", linewidth=2)
                ax.add_patch(rect)
    fig.tight_layout()
    return fig
