from __future__ import annotations

from typing import Any

from asra.exploration.visitation_memory import VisitationMemory


class NoveltyScorer:
    """State and edge novelty for exploration prioritization."""

    def __init__(
        self,
        alpha_object: float = 0.3,
        beta_frontier: float = 0.2,
    ) -> None:
        self.alpha_object = alpha_object
        self.beta_frontier = beta_frontier

    def state_novelty(
        self,
        state_hash: str,
        memory: VisitationMemory,
        object_scene: dict[str, Any] | None = None,
        frontier_bonus: float = 0.0,
    ) -> float:
        visits = memory.visit_count(state_hash)
        base = 1.0 / (1.0 + visits) ** 0.5
        obj_bonus = 0.0
        if object_scene and memory.object_fingerprint_seen(object_scene) <= 1:
            obj_bonus = self.alpha_object
        return base + obj_bonus + self.beta_frontier * frontier_bonus

    def edge_novelty(
        self,
        successor_hash: str,
        memory: VisitationMemory,
        reward: float = 0.0,
        dead_end: bool = False,
        object_scene: dict[str, Any] | None = None,
        gamma: float = 0.1,
        delta: float = 0.5,
    ) -> float:
        n = self.state_novelty(successor_hash, memory, object_scene=object_scene)
        reward_term = gamma * max(0.0, reward)
        penalty = delta if dead_end else 0.0
        return max(0.0, n + reward_term - penalty)
