from __future__ import annotations

from collections import Counter


class StuckDetector:
    def __init__(self, repeat_threshold: int = 4) -> None:
        self.visit_counts: Counter = Counter()
        self.repeat_threshold = repeat_threshold

    def observe(self, state_hash: str) -> None:
        self.visit_counts[state_hash] += 1

    def is_stuck(self, state_hash: str) -> bool:
        return self.visit_counts[state_hash] >= self.repeat_threshold
