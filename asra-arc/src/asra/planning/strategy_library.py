from __future__ import annotations

import random
from typing import Any

from asra.planning.schemas import Plan, PlanStep, Strategy


DEFAULT_STRATEGIES: list[Strategy] = [
    Strategy("reach_target", "Navigate to target", ["translate"], 1.2),
    Strategy("collect", "Collect tokens", ["delete_object", "translate"], 1.1),
    Strategy("align", "Align objects", ["localized_transform"], 1.0),
    Strategy("avoid", "Avoid hazards", ["no_op", "translate"], 0.9),
    Strategy("unlock", "Unlock passages", ["create_object", "recolor"], 1.0),
    Strategy("transform", "Transform grid", ["multi_cell_transform", "recolor"], 1.1),
    Strategy("sequence", "Multi-step sequence", ["translate", "recolor"], 1.0),
    Strategy("explore", "Explore unknown", ["unknown"], 0.7),
]


class StrategyLibrary:
    def __init__(self) -> None:
        self.strategies = list(DEFAULT_STRATEGIES)

    def match(self, goal_template_id: str | None) -> Strategy:
        mapping = {
            "move_to_target": "reach_target",
            "collect_tokens": "collect",
            "match_pattern": "transform",
            "avoid_hazard": "avoid",
            "unlock_passage": "unlock",
            "transform_to_goal": "transform",
        }
        name = mapping.get(goal_template_id or "", "explore")
        for s in self.strategies:
            if s.name == name:
                return s
        return self.strategies[-1]

    def score_action(self, strategy: Strategy, semantic_label: str) -> float:
        if semantic_label in strategy.preferred_semantics:
            return strategy.priority
        if semantic_label == "unknown":
            return strategy.priority * 0.5
        return 0.0


class MCTSPlannerLite:
    """Lightweight rollouts over candidate actions using semantic scores."""

    def __init__(self, rollouts: int = 8) -> None:
        self.rollouts = rollouts
        self.library = StrategyLibrary()

    def plan_step(
        self,
        candidates: list[str],
        semantic_fn: Any,
        state_hash: str,
        goal_template: str | None,
    ) -> PlanStep:
        strategy = self.library.match(goal_template)
        scores: dict[str, float] = {}
        for action in candidates:
            sem = semantic_fn(state_hash, action)
            label = sem.get("semantic_label", "unknown")
            base = self.library.score_action(strategy, label)
            noise = random.random() * 0.05
            scores[action] = base + float(sem.get("confidence") or 0) * 0.3 + noise
        best = max(scores.items(), key=lambda kv: kv[1])
        return PlanStep(best[0], None, best[1], f"mcts_lite:{strategy.name}")
