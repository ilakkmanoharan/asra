from __future__ import annotations

from collections import deque
from typing import Any


class ReplayBuffer:
    def __init__(self, maxlen: int = 10000) -> None:
        self._items: deque[dict[str, Any]] = deque(maxlen=maxlen)

    def add(self, transition: dict[str, Any]) -> None:
        self._items.append(transition)

    def sample_recent(self, n: int = 10) -> list[dict[str, Any]]:
        return list(self._items)[-n:]

    def __len__(self) -> int:
        return len(self._items)
