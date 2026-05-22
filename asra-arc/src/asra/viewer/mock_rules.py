"""Documented mock-environment rules for guided tutorial explanations."""

from __future__ import annotations

from typing import Any

from asra.env.action_space import SUPPORTED_ACTIONS

COLOR_NAMES = {0: "black (0)", 1: "blue (1)", 2: "red (2)", 3: "green (3)"}
COLOR_SHORT = {0: "black", 1: "blue", 2: "red", 3: "green"}
START_GRID = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]

# Human-readable position names (mock grid 3×3)
CELL_POSITION: dict[tuple[int, int], str] = {
    (0, 0): "top-left",
    (1, 0): "top-center",
    (2, 0): "top-right",
    (0, 1): "middle-left",
    (1, 1): "center",
    (2, 1): "middle-right",
    (0, 2): "bottom-left",
    (1, 2): "bottom-center",
    (2, 2): "bottom-right",
}


def action_semantic_label(action: str) -> str:
    """Plain-English line shown as ACTION = …"""
    if action == "RESET":
        return "RESET — restore starting grid (no cell movement)"
    cell = action_target_cell(action)
    if cell is None:
        return action
    pos = CELL_POSITION.get(cell, f"({cell[0]},{cell[1]})")
    return f"{action} — cycle color at {pos} cell (in-place, not a slide)"


def movement_description(changed_cells: list[dict[str, Any]]) -> str:
    if not changed_cells:
        return "MOVEMENT: none (grid unchanged)"
    if len(changed_cells) == 1:
        c = changed_cells[0]
        pos = CELL_POSITION.get((c["x"], c["y"]), f"({c['x']},{c['y']})")
        return (
            f"MOVEMENT: color change at {pos} — "
            f"{COLOR_SHORT.get(c['from'], c['from'])} → {COLOR_SHORT.get(c['to'], c['to'])} "
            f"(value {c['from']} → {c['to']})"
        )
    return f"MOVEMENT: {len(changed_cells)} cells changed"


def action_index(action: str) -> int | None:
    if action not in SUPPORTED_ACTIONS:
        return None
    return SUPPORTED_ACTIONS.index(action)


def action_target_cell(action: str) -> tuple[int, int] | None:
    if action not in SUPPORTED_ACTIONS[1:]:
        return None
    idx = SUPPORTED_ACTIONS.index(action) - 1
    return idx % 3, idx // 3


def apply_mock_action(grid: list[list[int]], action: str) -> list[list[int]]:
    """Same transition logic as MockArcAGI3Environment.step (grid only)."""
    if action == "RESET":
        return [row[:] for row in START_GRID]
    cell = action_target_cell(action)
    if cell is None:
        return [row[:] for row in grid]
    x, y = cell
    out = [row[:] for row in grid]
    out[y][x] = (out[y][x] + 1) % 4
    return out


def action_formula_markdown(action: str) -> str:
    if action == "RESET":
        return (
            "**RESET**\n\n"
            "```text\n"
            "next_grid = START_GRID\n"
            "START_GRID = center cell (1,1) = blue(1), all others black(0)\n"
            "```"
        )
    if action not in SUPPORTED_ACTIONS[1:]:
        return f"Unknown action `{action}`"
    idx = SUPPORTED_ACTIONS.index(action) - 1
    x, y = idx % 3, idx // 3
    return (
        f"**{action}** — index `i = {idx}` (because `SUPPORTED_ACTIONS.index('{action}') - 1`)\n\n"
        "```text\n"
        f"x = i % 3  →  {x}\n"
        f"y = i // 3  →  {y}\n"
        f"next[y][x] = (grid[y][x] + 1) % 4   # color cycle: 0→1→2→3→0\n"
        "```\n\n"
        f"Only **cell ({x}, {y})** changes; all other cells stay the same."
    )


def describe_cell_change(before: int, after: int, x: int, y: int) -> str:
    return (
        f"Cell **({x}, {y})**: {COLOR_NAMES.get(before, str(before))} → "
        f"{COLOR_NAMES.get(after, str(after))}  \n"
        f"Formula: `({before} + 1) % 4 = {after}`"
    )


def explain_transition(row: dict[str, Any]) -> str:
    action = row["action"]["name"]
    state = row["state"]["grid"]
    nxt = row["next_state"]["grid"]
    diff = row.get("diff", {})
    changed = diff.get("changed_cells", [])
    lines = [
        f"The agent logged **`{action}`** on this frame.",
        f"Reward **{row.get('reward', 0)}** · terminal **{row.get('terminal_state')}** · "
        f"status **{row['next_state'].get('status', '—')}**.",
    ]
    if action == "RESET":
        if not changed:
            lines.append(
                "The grid was **already** the start configuration, so RESET is a **no-op**: "
                "before and after are identical and `num_changed_cells = 0`. "
                "ASRA still records the step because every action is experience."
            )
        else:
            lines.append(
                "RESET restored (or moved toward) the **start grid**. "
                f"{len(changed)} cell(s) changed to match the canonical start."
            )
    elif len(changed) == 1:
        c = changed[0]
        lines.append(
            f"`{action}` targets a **single cell** under mock rules. "
            + describe_cell_change(c["from"], c["to"], c["x"], c["y"])
        )
        sim = apply_mock_action(state, action)
        if sim == nxt:
            lines.append("Simulated mock formula **matches** the logged `next_state` grid.")
        else:
            lines.append("Note: logged next state may differ if this row came from a non-mock run.")
    elif len(changed) == 0:
        lines.append("No cells changed on this frame.")
    else:
        lines.append(f"**{len(changed)}** cells changed.")
    return "\n\n".join(lines)


def preview_next_step_markdown(current: dict[str, Any], nxt_row: dict[str, Any] | None, frame_index: int) -> str:
    if nxt_row is None:
        return "**End of tutorial.** No further frame in this 10-step slice."
    action = nxt_row["action"]["name"]
    state = nxt_row["state"]["grid"]
    predicted = apply_mock_action(state, action)
    parts = [
        f"### Up next — frame {frame_index + 1} (log index {frame_index + 1})",
        f"The next logged action will be **`{action}`**.",
        action_formula_markdown(action),
        "**Why the next visual will look that way**",
    ]
    cell = action_target_cell(action)
    if action == "RESET":
        parts.append(
            "The environment will replace the grid with the start pattern. "
            "If the current grid is already the start, you will see **no change** again."
        )
    elif cell:
        x, y = cell
        v = state[y][x]
        after_v = predicted[y][x]
        parts.append(
            f"Before that action, cell ({x}, {y}) holds **{COLOR_NAMES.get(v, v)}**. "
            f"After applying the formula it becomes **{COLOR_NAMES.get(after_v, after_v)}**. "
            "Every other cell should look the same as in the “before” panel of that frame."
        )
    parts.append(
        f"Logged `step_index` on that row: **{nxt_row.get('step_index', '—')}** · "
        f"policy note: `{nxt_row.get('metadata', {}).get('policy', '—')}`"
    )
    return "\n\n".join(parts)
