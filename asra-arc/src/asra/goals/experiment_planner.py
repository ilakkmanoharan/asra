from __future__ import annotations

from typing import Any, Protocol

from asra.goals.schemas import ExperimentPlan, GoalHypothesis


class SemanticsProvider(Protocol):
    def infer(self, state_hash: str, action: str) -> dict[str, Any]: ...


class ExperimentPlanner:
    def __init__(self) -> None:
        self._plan_counter = 0

    def _next_id(self) -> str:
        self._plan_counter += 1
        return f"exp_{self._plan_counter}"

    def plan(
        self,
        state_hash: str,
        candidates: list[str],
        ranked_hypotheses: list[GoalHypothesis],
        semantics: SemanticsProvider,
    ) -> ExperimentPlan:
        top = ranked_hypotheses[:2]
        scores: dict[str, float] = {}
        for action in candidates:
            sem = semantics.infer(state_hash, action)
            label = sem.get("semantic_label", "unknown")
            unc = float(sem.get("uncertainty") or 0.0)
            if len(top) < 2:
                scores[action] = unc
                continue
            m1 = 1.0 if label in top[0].preferred_semantics else 0.0
            m2 = 1.0 if label in top[1].preferred_semantics else 0.0
            scores[action] = unc * abs(m1 - m2)
        chosen = max(scores.items(), key=lambda kv: kv[1])[0] if scores else (candidates[0] if candidates else "")
        return ExperimentPlan(
            plan_id=self._next_id(),
            state_hash=state_hash,
            candidate_actions=list(candidates),
            target_hypotheses=[h.hypothesis_id for h in top],
            discrimination_scores=scores,
            chosen_action=chosen,
            rationale="maximize hypothesis discrimination × uncertainty",
        )

    def discrimination_bonus(
        self,
        state_hash: str,
        action: str,
        ranked_hypotheses: list[GoalHypothesis],
        semantics: SemanticsProvider,
    ) -> float:
        plan = self.plan(state_hash, [action], ranked_hypotheses, semantics)
        return plan.discrimination_scores.get(action, 0.0)
