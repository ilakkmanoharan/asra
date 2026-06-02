from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


SubgoalStatus = Literal["pending", "active", "completed"]


@dataclass
class ExplorationNode:
    node_id: str
    state_hash: str
    visit_count: int = 0
    first_seen_step: int = 0
    last_seen_step: int = 0
    terminal: bool = False
    object_summary: dict[str, Any] | None = None
    grid_shape: tuple[int, int] = (0, 0)
    frontier_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["grid_shape"] = list(self.grid_shape)
        return d


@dataclass
class ExplorationEdge:
    from_id: str
    to_id: str
    action: str
    count: int = 0
    avg_reward: float = 0.0
    avg_novelty_gain: float = 0.0
    usefulness_score: float = 0.0
    dead_end: bool = False
    _reward_sum: float = field(default=0.0, repr=False)
    _novelty_sum: float = field(default=0.0, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "from": self.from_id,
            "to": self.to_id,
            "action": self.action,
            "count": self.count,
            "avg_reward": self.avg_reward,
            "avg_novelty_gain": self.avg_novelty_gain,
            "usefulness_score": self.usefulness_score,
            "dead_end": self.dead_end,
        }


@dataclass
class SubgoalState:
    subgoal_id: str
    index: int
    description: str
    status: SubgoalStatus = "pending"
    entered_at_step: int | None = None
    completed_at_step: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StrategyPattern:
    strategy_id: str
    name: str
    precondition: dict[str, Any]
    action_sequence: list[str]
    success_count: int = 0
    source_env: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
