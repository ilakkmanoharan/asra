from __future__ import annotations

from typing import Any

from asra.exploration.schemas import SubgoalState


class UsefulnessScorer:
    """Progress-oriented action scoring (reward, frontier, subgoals, dead-ends)."""

    def __init__(
        self,
        w_reward: float = 1.0,
        w_frontier: float = 0.8,
        w_subgoal: float = 1.2,
        w_dead_end: float = 1.0,
        w_object_delta: float = 0.3,
    ) -> None:
        self.w_reward = w_reward
        self.w_frontier = w_frontier
        self.w_subgoal = w_subgoal
        self.w_dead_end = w_dead_end
        self.w_object_delta = w_object_delta

    def score(
        self,
        reward_delta: float = 0.0,
        frontier_gain: float = 0.0,
        subgoal: SubgoalState | None = None,
        dead_end: bool = False,
        object_delta: int | None = None,
    ) -> float:
        subgoal_progress = 0.0
        if subgoal and subgoal.status == "completed":
            subgoal_progress = 1.0
        elif subgoal and subgoal.status == "active":
            subgoal_progress = 0.3
        obj_term = 0.0
        if object_delta is not None and object_delta != 0:
            obj_term = self.w_object_delta * (1.0 if object_delta > 0 else 0.5)
        total = (
            self.w_reward * reward_delta
            + self.w_frontier * frontier_gain
            + self.w_subgoal * subgoal_progress
            + obj_term
        )
        if dead_end:
            total -= self.w_dead_end
        return total
