"""Compact Phase 3 exploration hints for Kaggle ARC-AGI-3 agent (v0.5-phase3).

Mirrors library novelty/usefulness scoring without full asra-arc install.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Dict, List, Optional


class CompactExplorationHints:
    """Visit memory + frontier bonus for action scoring on competition agent."""

    def __init__(self, recent_window: int = 20) -> None:
        self.visit_counts: Dict[str, int] = defaultdict(int)
        self.recent: deque[str] = deque(maxlen=recent_window)
        self.edge_stats: Dict[tuple[str, str], Dict[str, float]] = defaultdict(lambda: {"novelty": 0.0, "usefulness": 0.0, "n": 0.0})

    def observe(self, state_hash: str, next_hash: str, action: str, reward: float, changed_cells: int) -> None:
        self.visit_counts[state_hash] += 1
        self.visit_counts[next_hash] += 1
        self.recent.append(next_hash)
        novelty = 1.0 / (1.0 + self.visit_counts[next_hash]) ** 0.5
        usefulness = float(reward) + (0.5 if changed_cells else 0.0)
        key = (state_hash, action)
        stats = self.edge_stats[key]
        stats["n"] += 1
        stats["novelty"] = ((stats["novelty"] * (stats["n"] - 1)) + novelty) / stats["n"]
        stats["usefulness"] = ((stats["usefulness"] * (stats["n"] - 1)) + usefulness) / stats["n"]

    def score_action(self, state_hash: str, action: str) -> float:
        visits = self.visit_counts[state_hash]
        frontier_bonus = 1.0 / (1.0 + visits) ** 0.5
        stats = self.edge_stats.get((state_hash, action))
        if stats and stats["n"] > 0:
            repeat_penalty = 1.0 if self.recent.count(state_hash) > 2 else 0.0
            return stats["novelty"] + stats["usefulness"] + frontier_bonus - repeat_penalty
        return frontier_bonus + 0.5

    def bias_available_actions(self, state_hash: str, actions: List[str]) -> Optional[str]:
        if not actions:
            return None
        scored = [(self.score_action(state_hash, action), action) for action in actions]
        scored.sort(reverse=True)
        return scored[0][1]

    def exploration_metadata(self, state_hash: str) -> Dict[str, Any]:
        return {
            "visit_count_before": self.visit_counts[state_hash],
            "frontier_node": self.visit_counts[state_hash] <= 2,
            "recent_unique": len(set(self.recent)),
        }
