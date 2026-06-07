from __future__ import annotations

from typing import Any, Protocol

from asra.goals.experiment_planner import ExperimentPlanner
from asra.goals.goals_store import GoalsStore
from asra.goals.hypothesis_ranker import HypothesisRanker


class SemanticsProvider(Protocol):
    def infer(self, state_hash: str, action: str) -> dict[str, Any]: ...


class GoalHypothesisPolicyV4:
    """Phase 5 policy: Phase 4 semantics + goal ranking + experiment discrimination."""

    def __init__(
        self,
        semantics: SemanticsProvider,
        *,
        goal_weight: float = 0.25,
        experiment_weight: float = 0.15,
    ) -> None:
        self.semantics = semantics
        self.store = GoalsStore()
        self.ranker = HypothesisRanker()
        self.planner = ExperimentPlanner()
        self.goal_weight = goal_weight
        self.experiment_weight = experiment_weight

    def score_action(
        self,
        game_id: str,
        state_hash: str,
        action: str,
        scene: dict[str, Any],
        base_score: float,
    ) -> tuple[float, dict[str, Any]]:
        hyps = self.store.ensure_game_hypotheses(game_id, scene)
        ranked = self.ranker.rank(hyps)
        sem = self.semantics.infer(state_hash, action)
        lead = ranked[0] if ranked else None
        goal_bonus = 0.0
        if lead and sem.get("semantic_label") in lead.preferred_semantics:
            goal_bonus = lead.progress_weights.get(str(sem.get("semantic_label")), 0.5)
        exp_bonus = self.planner.discrimination_bonus(state_hash, action, ranked, self.semantics)
        total = base_score + self.goal_weight * goal_bonus + self.experiment_weight * exp_bonus
        meta = {
            "semantic_label": sem.get("semantic_label"),
            "leading_template_id": lead.template_id if lead else None,
            "goal_bonus": goal_bonus,
            "experiment_bonus": exp_bonus,
        }
        return total, meta
