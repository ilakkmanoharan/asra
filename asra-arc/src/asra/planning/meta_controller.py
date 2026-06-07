from __future__ import annotations

from typing import Literal

ExploreExploitMode = Literal["explore", "exploit", "balanced"]


class MetaController:
    """Explore vs exploit given coverage and goal confidence."""

    def __init__(self, explore_threshold: float = 0.35) -> None:
        self.explore_threshold = explore_threshold
        self.steps = 0

    def mode(
        self,
        *,
        visit_count: int,
        goal_confidence: float,
        uncertainty: float,
    ) -> ExploreExploitMode:
        self.steps += 1
        if visit_count <= 2 or uncertainty > self.explore_threshold:
            return "explore"
        if goal_confidence > 0.7:
            return "exploit"
        return "balanced"

    def blend_weights(self, mode: ExploreExploitMode) -> dict[str, float]:
        if mode == "explore":
            return {"exploration": 1.2, "goal": 0.6, "plan": 0.4}
        if mode == "exploit":
            return {"exploration": 0.5, "goal": 1.3, "plan": 1.2}
        return {"exploration": 1.0, "goal": 1.0, "plan": 1.0}


class ResetPolicy:
    def should_reset(self, *, stuck_count: int, max_stuck: int = 5, actions: int, max_actions: int) -> bool:
        if stuck_count >= max_stuck:
            return True
        return actions >= max_actions


class PlanRepairSystem:
    def repair(self, plan_steps: list, failed_action: str) -> list:
        return [s for s in plan_steps if getattr(s, "action", None) != failed_action]
