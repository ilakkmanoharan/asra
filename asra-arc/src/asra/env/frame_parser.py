from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

VALID_STATUSES = {"NOT_FINISHED", "WIN", "GAME_OVER"}


@dataclass(frozen=True)
class Frame:
    game_id: str
    level_id: str
    step_index: int
    grid: list[list[int]]
    height: int
    width: int
    status: str = "NOT_FINISHED"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_frame(raw_frame: dict[str, Any]) -> Frame:
    if not isinstance(raw_frame, dict):
        raise ValueError("Frame must be a JSON object")

    grid = raw_frame.get("grid") or raw_frame.get("board") or raw_frame.get("state")
    _validate_grid(grid)

    status = raw_frame.get("status", raw_frame.get("terminal_status", "NOT_FINISHED"))
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")

    height = len(grid)
    width = len(grid[0]) if height else 0
    metadata = dict(raw_frame.get("metadata") or {})
    metadata.setdefault("raw_frame_keys", sorted(raw_frame.keys()))
    metadata.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    metadata.setdefault("source", "arc-agi-3")

    return Frame(
        game_id=str(raw_frame.get("game_id", "unknown-game")),
        level_id=str(raw_frame.get("level_id", "unknown-level")),
        step_index=int(raw_frame.get("step_index", raw_frame.get("step", 0))),
        grid=[list(row) for row in grid],
        height=height,
        width=width,
        status=status,
        metadata=metadata,
    )


def _validate_grid(grid: Any) -> None:
    if grid is None:
        raise ValueError("Frame grid is required")
    if not isinstance(grid, list) or not grid or not all(isinstance(row, list) for row in grid):
        raise ValueError("Grid must be a non-empty list of rows")
    width = len(grid[0])
    if width == 0:
        raise ValueError("Grid rows must be non-empty")
    if len(grid) > 64 or width > 64:
        raise ValueError("Grid max size is 64x64")
    for row in grid:
        if len(row) != width:
            raise ValueError("Grid must be rectangular")
        for value in row:
            if not isinstance(value, int) or value < 0 or value > 15:
                raise ValueError("Grid cell values must be integers from 0 to 15")
