from __future__ import annotations

from collections import Counter
from typing import Any


def detect_dead_end(state_hash: str, action_reports: list[dict[str, Any]] | None = None, recent_states: list[str] | None = None, status: str = "NOT_FINISHED", novelty_attempts_without_gain: int = 0) -> dict[str, Any]:
    reports = action_reports or []
    recent_states = recent_states or []
    reasons: list[str] = []
    score = 0.0
    if status == "GAME_OVER":
        reasons.append("game_over")
        score += 1.0
    if reports and all(report.get("next_state_hash") == state_hash for report in reports):
        reasons.append("all_actions_return_same_state")
        score += 0.35
    if reports and all(report.get("changed_cells", 0) == 0 for report in reports):
        reasons.append("no_grid_change")
        score += 0.35
    if recent_states and Counter(recent_states).most_common(1)[0][1] >= 3:
        reasons.append("cycle_detected")
        score += 0.25
    if novelty_attempts_without_gain >= 5:
        reasons.append("no_novelty_after_attempts")
        score += 0.25
    if reports and len(reports) >= 8:
        reasons.append("all_actions_tested")
        score += 0.1
    score = round(min(score, 1.0), 6)
    return {"state_hash": state_hash, "dead_end_score": score, "reasons": reasons, "recommended_action": "RESET" if score >= 0.8 else None}
