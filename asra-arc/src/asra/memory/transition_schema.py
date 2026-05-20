from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from asra.env.action_space import action_index
from asra.env.frame_parser import Frame
from asra.utils.hashing import hash_state


@dataclass
class Transition:
    transition_id: str
    episode_id: str
    game_id: str
    level_id: str
    step_index: int
    state: dict[str, Any]
    action: dict[str, Any]
    next_state: dict[str, Any]
    reward: float
    terminal_state: bool
    diff: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def make_transition(
    episode_id: str,
    state: Frame,
    action: str,
    next_state: Frame,
    reward: float,
    diff: dict[str, Any],
    agent_version: str = "asra-v0.1",
    policy: str = "simple_exploration",
    notes: str = "",
) -> Transition:
    state_hash = hash_state(state.grid)
    next_state_hash = hash_state(next_state.grid)
    return Transition(
        transition_id=str(uuid4()),
        episode_id=episode_id,
        game_id=state.game_id,
        level_id=state.level_id,
        step_index=state.step_index,
        state={"grid": state.grid, "height": state.height, "width": state.width, "status": state.status, "state_hash": state_hash},
        action={"name": action, "index": action_index(action)},
        next_state={"grid": next_state.grid, "height": next_state.height, "width": next_state.width, "status": next_state.status, "state_hash": next_state_hash},
        reward=float(reward),
        terminal_state=next_state.status in {"WIN", "GAME_OVER"},
        diff=diff,
        metadata={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_version": agent_version,
            "policy": policy,
            "raw_action_semantics_known": False,
            "notes": notes,
        },
    )
