from __future__ import annotations

from collections import Counter
from typing import Any


def summarize_episode(episode_id: str, transitions: list[dict[str, Any]]) -> dict[str, Any]:
    if not transitions:
        return {"episode_id": episode_id, "game_id": "", "level_id": "", "num_steps": 0, "unique_states": 0, "num_cycles": 0, "num_dead_ends": 0, "final_status": "NOT_FINISHED", "total_reward": 0.0, "actions_used": {}}
    states = [row["state"]["state_hash"] for row in transitions] + [transitions[-1]["next_state"]["state_hash"]]
    counts = Counter(states)
    actions = Counter(row["action"]["name"] for row in transitions)
    return {
        "episode_id": episode_id,
        "game_id": transitions[0]["game_id"],
        "level_id": transitions[0]["level_id"],
        "num_steps": len(transitions),
        "unique_states": len(counts),
        "num_cycles": sum(1 for count in counts.values() if count > 1),
        "num_dead_ends": sum(1 for row in transitions if row.get("metadata", {}).get("dead_end_score", 0) >= 0.8),
        "final_status": transitions[-1]["next_state"].get("status", "NOT_FINISHED"),
        "total_reward": sum(float(row.get("reward", 0.0)) for row in transitions),
        "actions_used": dict(actions),
    }
