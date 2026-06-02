from __future__ import annotations

import heapq
from pathlib import Path
from typing import Any

from asra.utils.serialization import write_jsonl


class TransitionReplayBuffer:
    """Priority buffer of high-value transitions for analysis and replay."""

    def __init__(self, capacity: int = 500) -> None:
        self.capacity = capacity
        self._heap: list[tuple[float, int, dict[str, Any]]] = []
        self._seq = 0

    def push(self, transition: dict[str, Any], priority: float) -> None:
        self._seq += 1
        heapq.heappush(self._heap, (priority, self._seq, transition))
        if len(self._heap) > self.capacity:
            heapq.heappop(self._heap)

    def sample(self, k: int) -> list[dict[str, Any]]:
        ranked = sorted(self._heap, key=lambda item: item[0], reverse=True)[:k]
        return [item[2] for item in ranked]

    def export(self, path: str | Path) -> None:
        rows = [item[2] for item in sorted(self._heap, key=lambda item: item[0], reverse=True)]
        write_jsonl(path, rows)

    def __len__(self) -> int:
        return len(self._heap)
