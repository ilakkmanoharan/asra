from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FailureReport:
    episode_id: str
    failure_type: str
    count: int
    metadata: dict[str, Any] = field(default_factory=dict)


class FailureAnalyzer:
    def __init__(self) -> None:
        self.dead_ends: Counter = Counter()
        self.no_progress: Counter = Counter()

    def record(self, state_hash: str, action: str, changed_cells: int, reward: float) -> None:
        key = f"{state_hash}:{action}"
        if changed_cells == 0 and reward <= 0:
            self.dead_ends[key] += 1
            self.no_progress[key] += 1

    def top_failures(self, n: int = 10) -> list[FailureReport]:
        reports = []
        for key, count in self.dead_ends.most_common(n):
            reports.append(FailureReport(key, "dead_end", count))
        return reports
