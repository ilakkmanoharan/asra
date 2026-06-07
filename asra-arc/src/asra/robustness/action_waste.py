from __future__ import annotations

from collections import Counter


class ActionWasteReducer:
    def __init__(self, max_repeat: int = 3) -> None:
        self.action_counts: Counter = Counter()
        self.max_repeat = max_repeat

    def observe(self, state_hash: str, action: str) -> None:
        self.action_counts[(state_hash, action)] += 1

    def waste_penalty(self, state_hash: str, action: str) -> float:
        n = self.action_counts[(state_hash, action)]
        if n >= self.max_repeat:
            return float(n - self.max_repeat + 1) * 0.2
        return 0.0
