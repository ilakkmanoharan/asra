from __future__ import annotations

from typing import Any, Protocol

from asra.planning.bfs_planner import BFSPlanner
from asra.planning.meta_controller import MetaController
from asra.planning.strategy_library import MCTSPlannerLite, StrategyLibrary


class SemanticsProvider(Protocol):
    def infer(self, state_hash: str, action: str) -> dict[str, Any]: ...


class PlanningPolicyV5:
    """Phase 6: planning hints on top of Phase 5 goal policy."""

    def __init__(self, semantics: SemanticsProvider) -> None:
        self.semantics = semantics
        self.bfs = BFSPlanner()
        self.mcts = MCTSPlannerLite()
        self.meta = MetaController()
        self.strategies = StrategyLibrary()

    def observe_transition(self, state_hash: str, action: str, next_hash: str) -> None:
        self.bfs.observe(state_hash, action, next_hash)

    def plan_bonus(
        self,
        state_hash: str,
        action: str,
        goal_template: str | None,
        visit_count: int,
    ) -> float:
        sem = self.semantics.infer(state_hash, action)
        strategy = self.strategies.match(goal_template)
        base = self.strategies.score_action(strategy, sem.get("semantic_label", "unknown"))
        mode = self.meta.mode(
            visit_count=visit_count,
            goal_confidence=float(sem.get("confidence") or 0),
            uncertainty=float(sem.get("uncertainty") or 1),
        )
        weights = self.meta.blend_weights(mode)
        return base * weights["plan"]
