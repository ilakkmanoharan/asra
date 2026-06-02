from __future__ import annotations

from typing import Any

from asra.causality.counterfactual import CounterfactualSimulator
from asra.causality.semantics_store import SemanticsStore
from asra.exploration.exploration_graph import ExplorationGraph
from asra.exploration.policy_v2 import ExplorationPolicyV2
from asra.exploration.schemas import SubgoalState
from asra.exploration.visitation_memory import VisitationMemory


class CausalExplorationPolicyV3(ExplorationPolicyV2):
    """Phase 3 exploration + Phase 4 semantics/uncertainty/prediction hints."""

    name = "exploration_v3"

    def __init__(
        self,
        semantics: SemanticsStore | None = None,
        *,
        semantics_weight: float = 0.35,
        prediction_weight: float = 0.25,
        uncertainty_weight: float = 0.4,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.semantics = semantics or SemanticsStore()
        self.semantics_weight = semantics_weight
        self.prediction_weight = prediction_weight
        self.uncertainty_weight = uncertainty_weight
        self.counterfactual = CounterfactualSimulator(self.semantics.model)
        self._game_id = "unknown"

    def set_game_id(self, game_id: str) -> None:
        self._game_id = game_id

    def _semantics_bonus(self, state_hash: str, action: str) -> tuple[float, dict[str, Any]]:
        sig = self.semantics.get_signature(self._game_id, state_hash, action)
        if sig is None or sig.observation_count == 0:
            return 0.0, {"semantic_label": "unknown", "confidence": 0.0, "uncertainty": 1.0}
        meta = self.semantics.causality_metadata(sig)
        progress = min(1.0, sig.cell_change_mean / 10.0) + min(1.0, abs(sig.object_delta_mean))
        bonus = (
            self.semantics_weight * sig.confidence
            + self.prediction_weight * progress
            + self.uncertainty_weight * float(meta["uncertainty"])
        )
        return bonus, meta

    def select_action(
        self,
        state_hash: str,
        available_actions: list[str],
        graph: ExplorationGraph,
        memory: VisitationMemory,
        subgoal: SubgoalState | None = None,
        object_scene: dict[str, Any] | None = None,
        precondition: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        base = super().select_action(
            state_hash,
            available_actions,
            graph,
            memory,
            subgoal=subgoal,
            object_scene=object_scene,
            precondition=precondition,
        )
        action = base["selected_action"]
        bonus, sem_meta = self._semantics_bonus(state_hash, action)
        base["score"] = float(base.get("score", 0.0)) + bonus
        base["causality"] = sem_meta
        base["policy"] = self.name
        return base
