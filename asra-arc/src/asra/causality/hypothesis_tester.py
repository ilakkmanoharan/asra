from __future__ import annotations

import hashlib
from typing import Any

from asra.causality.schemas import ActionEffectSignature, CausalHypothesis


class HypothesisTester:
    """Maintain and update causal hypotheses from effect signatures."""

    def __init__(self, min_support: int = 3, refute_tolerance: float = 2.0) -> None:
        self.min_support = min_support
        self.refute_tolerance = refute_tolerance
        self._hypotheses: dict[str, CausalHypothesis] = {}

    def _hypothesis_id(self, game_id: str, action: str, effect: str) -> str:
        raw = f"{game_id}:{action}:{effect}"
        return "hyp_" + hashlib.sha256(raw.encode()).hexdigest()[:10]

    def upsert_from_signature(self, signature: ActionEffectSignature) -> CausalHypothesis:
        effect = signature.semantic_label
        hid = self._hypothesis_id(signature.game_id, signature.action, effect)
        hyp = self._hypotheses.get(hid)
        if hyp is None:
            hyp = CausalHypothesis(
                hypothesis_id=hid,
                game_id=signature.game_id,
                action=signature.action,
                predicted_effect=effect,
                precondition={"state_hash": signature.state_hash},
                support=signature.observation_count,
            )
        else:
            hyp.support = max(hyp.support, signature.observation_count)
        hyp.status = self._status(hyp)
        self._hypotheses[hid] = hyp
        return hyp

    def test_observation(
        self,
        game_id: str,
        action: str,
        observed_effect: str,
        *,
        changed_cells: float,
        expected_cells: float,
    ) -> CausalHypothesis | None:
        matching = [
            h for h in self._hypotheses.values()
            if h.game_id == game_id and h.action == action and h.status in {"active", "weak", "confirmed"}
        ]
        if not matching:
            return None
        hyp = matching[0]
        if observed_effect == hyp.predicted_effect:
            hyp.support += 1
        elif abs(changed_cells - expected_cells) > self.refute_tolerance:
            hyp.refute += 1
        hyp.status = self._status(hyp)
        return hyp

    def _status(self, hyp: CausalHypothesis) -> str:
        if hyp.refute >= 2 and hyp.refute > hyp.support:
            return "refuted"
        if hyp.support >= self.min_support:
            return "confirmed"
        if hyp.support >= 1:
            return "weak"
        return "active"

    def get(self, hypothesis_id: str) -> CausalHypothesis | None:
        return self._hypotheses.get(hypothesis_id)

    def for_action(self, game_id: str, action: str) -> list[CausalHypothesis]:
        return [h for h in self._hypotheses.values() if h.game_id == game_id and h.action == action]

    def all_hypotheses(self) -> list[CausalHypothesis]:
        return list(self._hypotheses.values())

    def to_dict(self) -> dict[str, Any]:
        return {"hypotheses": [h.to_dict() for h in self.all_hypotheses()]}
