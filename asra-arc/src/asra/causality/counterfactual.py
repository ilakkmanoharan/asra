from __future__ import annotations

from asra.causality.schemas import CounterfactualResult
from asra.causality.transition_model import CausalTransitionModel


class CounterfactualSimulator:
    """What-if alternate action from the same state — lookup then model fallback."""

    def __init__(self, model: CausalTransitionModel | None = None) -> None:
        self.model = model or CausalTransitionModel()

    def simulate(
        self,
        game_id: str,
        state_hash: str,
        actual_action: str,
        alt_action: str,
    ) -> CounterfactualResult:
        pred = self.model.predict(game_id, state_hash, alt_action)
        if pred.support_count > 0:
            return CounterfactualResult(
                state_hash=state_hash,
                actual_action=actual_action,
                alt_action=alt_action,
                predicted_changed_cells=pred.predicted_changed_cells,
                predicted_object_delta=pred.predicted_object_delta,
                predicted_transforms=pred.predicted_transforms,
                confidence=pred.probability,
                source="observed" if pred.probability >= 0.8 else "model",
            )
        return CounterfactualResult(
            state_hash=state_hash,
            actual_action=actual_action,
            alt_action=alt_action,
            predicted_changed_cells=0.0,
            predicted_object_delta=0.0,
            predicted_transforms=[],
            confidence=0.0,
            source="none",
        )
