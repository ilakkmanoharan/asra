from __future__ import annotations

from asra.goals.schemas import GoalHypothesis, ProgressSignal


class HypothesisRanker:
    def score(self, hypothesis: GoalHypothesis) -> float:
        return (
            hypothesis.progress_score
            + 2.0 * hypothesis.support
            - 1.5 * hypothesis.refute
            + hypothesis.confidence
        )

    def rank(self, hypotheses: list[GoalHypothesis]) -> list[GoalHypothesis]:
        ranked = sorted(hypotheses, key=self.score, reverse=True)
        for i, h in enumerate(ranked):
            if h.status in ("refuted", "confirmed"):
                continue
            h.status = "leading" if i == 0 else "active"
        return ranked

    def update_from_signal(self, hypothesis: GoalHypothesis, signal: ProgressSignal) -> None:
        label = signal.semantic_label
        w = hypothesis.progress_weights
        delta = 0.0
        if label in hypothesis.preferred_semantics:
            delta += w.get(label, 0.5)
        if signal.signal_type == "reward":
            delta += w.get("reward", 0.0)
        if signal.signal_type == "level_up":
            delta += w.get("level_up", 0.0)
            hypothesis.support += 1
        elif signal.signal_type == "win":
            hypothesis.support += 2
            hypothesis.status = "confirmed"
        hypothesis.progress_score += delta

    def refute_mismatch(self, hypothesis: GoalHypothesis, semantic_label: str, had_reward: bool) -> None:
        if not had_reward and semantic_label not in hypothesis.preferred_semantics and semantic_label != "unknown":
            hypothesis.refute += 1
            if hypothesis.refute >= 3 and hypothesis.support == 0:
                hypothesis.status = "refuted"
