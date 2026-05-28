from __future__ import annotations

from collections import defaultdict
from typing import Any

from asra.env.action_space import SUPPORTED_ACTIONS


class SimpleExplorationPolicy:
    name = "simple_exploration"

    def __init__(self) -> None:
        self.action_memory: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
        self.recent_states: list[str] = []

    def observe(self, transition: dict[str, Any]) -> None:
        state_hash = transition["state"]["state_hash"]
        action = transition["action"]["name"]
        self.action_memory[state_hash][action].append(transition)
        self.recent_states.append(transition["next_state"]["state_hash"])
        self.recent_states = self.recent_states[-20:]

    def select_action(self, state_hash: str, actions: list[str] | None = None, dead_end_score: float = 0.0) -> dict[str, Any]:
        actions = actions or SUPPORTED_ACTIONS
        if dead_end_score >= 0.8 and "RESET" in actions:
            return {"selected_action": "RESET", "reason": "high_dead_end_score", "score": 10.0}
        scored = []
        for action in actions:
            observations = self.action_memory[state_hash].get(action, [])
            score = 0.0
            reason = "observed_action"
            if not observations:
                score += 2.0
                reason = "untested_action_with_high_novelty_potential"
            for transition in observations:
                next_hash = transition["next_state"]["state_hash"]
                if next_hash not in self.recent_states:
                    score += 1.0
                score += float(transition.get("diff", {}).get("change_ratio", 0.0))
                if transition["next_state"].get("status") == "WIN":
                    score += 5.0
                if transition["next_state"].get("status") == "GAME_OVER":
                    score -= 5.0
                if transition.get("diff", {}).get("num_changed_cells", 0) == 0:
                    score -= 0.5
                if self.recent_states.count(next_hash) > 1:
                    score -= 1.0
            scored.append((score, action, reason))
        score, action, reason = max(scored, key=lambda item: (item[0], -SUPPORTED_ACTIONS.index(item[1]) if item[1] in SUPPORTED_ACTIONS else 0))
        return {"selected_action": action, "reason": reason, "score": score}
