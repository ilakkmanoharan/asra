from __future__ import annotations

import math

from asra.causality.schemas import ActionEffectSignature


class UncertaintyScorer:
    """Epistemic uncertainty per (state, action) — decreases with observations."""

    def __init__(self, weak_hypothesis_weight: float = 0.25, variance_weight: float = 0.15) -> None:
        self.weak_hypothesis_weight = weak_hypothesis_weight
        self.variance_weight = variance_weight

    def score(
        self,
        signature: ActionEffectSignature,
        *,
        hypothesis_status: str | None = None,
    ) -> float:
        n = max(0, signature.observation_count)
        base = 1.0 / math.sqrt(1.0 + n)
        weak_bonus = self.weak_hypothesis_weight if hypothesis_status == "weak" else 0.0
        var_bonus = self.variance_weight * min(1.0, signature.cell_change_std / max(1.0, signature.cell_change_mean + 1.0))
        return min(1.0, base + weak_bonus + var_bonus)

    def score_from_counts(self, observation_count: int, cell_change_std: float = 0.0) -> float:
        sig = ActionEffectSignature(
            action="",
            game_id="",
            state_hash="",
            observation_count=observation_count,
            cell_change_std=cell_change_std,
        )
        return self.score(sig)
