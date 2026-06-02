from __future__ import annotations

from typing import Any

MINIGRID_ACTION_NAMES = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]


def encode_minigrid_grid(env: Any) -> list[list[int]]:
    """Encode MiniGrid full grid into ASRA integer grid (values 0–15).

    Appends a synthetic row with agent pose (and carry flag) so state hashes
    distinguish positions in otherwise identical layouts.
    """
    unwrapped = env.unwrapped
    grid = unwrapped.grid
    encoded = grid.encode()
    matrix: list[list[int]] = []
    for y in range(grid.height):
        row: list[int] = []
        for x in range(grid.width):
            obj_type, color, state = (int(encoded[y][x][i]) for i in range(3))
            row.append(min(15, obj_type + color + state))
        matrix.append(row)

    ax, ay = int(unwrapped.agent_pos[0]), int(unwrapped.agent_pos[1])
    agent_row = [0] * grid.width
    agent_row[0] = min(15, ax)
    agent_row[1] = min(15, ay)
    agent_row[2] = min(15, int(unwrapped.agent_dir))
    carrying = getattr(unwrapped, "carrying", None)
    agent_row[3] = 1 if carrying is not None else 0
    matrix.append(agent_row)
    return matrix


def grid_has_open_door(env: Any) -> bool:
    grid = env.unwrapped.grid
    for y in range(grid.height):
        for x in range(grid.width):
            cell = grid.get(x, y)
            if cell is not None and getattr(cell, "type", None) == "door" and getattr(cell, "is_open", False):
                return True
    return False


def agent_carrying_type(env: Any) -> str | None:
    carrying = getattr(env.unwrapped, "carrying", None)
    if carrying is None:
        return None
    return str(getattr(carrying, "type", ""))


def minigrid_precondition(env: Any, env_id: str = "") -> dict[str, Any]:
    """Precondition tags for strategy matching."""
    carrying_type = agent_carrying_type(env)
    has_key = carrying_type == "key"
    door_open = grid_has_open_door(env)
    is_doorkey = "DoorKey" in env_id or "doorkey" in env_id.lower()
    return {
        "env_type": "doorkey" if is_doorkey else "minigrid",
        "has_key": has_key,
        "carrying": carrying_type is not None,
        "carrying_type": carrying_type or "",
        "door_open": door_open,
    }


def asra_action_names(action_count: int) -> list[str]:
    return [f"ACTION{i + 1}" for i in range(action_count)]


def minigrid_action_label(action_idx: int) -> str:
    if 0 <= action_idx < len(MINIGRID_ACTION_NAMES):
        return MINIGRID_ACTION_NAMES[action_idx]
    return f"ACTION{action_idx + 1}"


def status_from_gym(terminated: bool, truncated: bool) -> str:
    if terminated:
        return "WIN"
    if truncated:
        return "GAME_OVER"
    return "NOT_FINISHED"
