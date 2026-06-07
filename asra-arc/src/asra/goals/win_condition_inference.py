from __future__ import annotations

from typing import Any

from asra.goals.hypothesis_ranker import HypothesisRanker
from asra.goals.schemas import GoalHypothesis


class WinConditionInference:
    """Score hypotheses against terminal / near-terminal transition sequences."""

    def __init__(self) -> None:
        self.ranker = HypothesisRanker()

    def score_sequence(
        self,
        hypotheses: list[GoalHypothesis],
        semantic_sequence: list[str],
        had_win: bool,
    ) -> list[GoalHypothesis]:
        for h in hypotheses:
            matches = sum(1 for s in semantic_sequence if s in h.preferred_semantics)
            h.progress_score += float(matches)
            if had_win and matches >= max(1, len(semantic_sequence) // 3):
                h.support += 1
        return self.ranker.rank(hypotheses)

    def infer_from_episode_tail(
        self,
        hypotheses: list[GoalHypothesis],
        transitions: list[dict[str, Any]],
        tail: int = 5,
    ) -> GoalHypothesis | None:
        tail_transitions = transitions[-tail:] if transitions else []
        semantics: list[str] = []
        had_win = False
        for t in tail_transitions:
            meta = t.get("metadata") or {}
            causality = meta.get("causality") or {}
            semantics.append(str(causality.get("semantic_label") or "unknown"))
            if t.get("terminal") or (t.get("reward") or 0) > 0:
                had_win = True
        ranked = self.score_sequence(hypotheses, semantics, had_win)
        return ranked[0] if ranked else None
