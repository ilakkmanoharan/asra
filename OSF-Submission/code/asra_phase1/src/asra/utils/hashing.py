from __future__ import annotations

import hashlib
import json
from typing import Any


def hash_state(grid: list[list[int]], metadata: dict[str, Any] | None = None) -> str:
    payload: dict[str, Any] = {
        "height": len(grid),
        "width": len(grid[0]) if grid else 0,
        "grid": grid,
    }
    if metadata:
        stable_metadata = {k: v for k, v in metadata.items() if k != "timestamp"}
        if stable_metadata:
            payload["metadata"] = stable_metadata
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
