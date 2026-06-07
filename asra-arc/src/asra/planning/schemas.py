from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

StrategyName = Literal[
    "reach_target", "collect", "align", "avoid", "unlock", "transform", "sequence", "explore"
]
PlannerMode = Literal["bfs", "greedy", "mcts_lite"]


@dataclass
class PlanStep:
    action: str
    predicted_state_hash: str | None
    score: float
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Plan:
    plan_id: str
    game_id: str
    start_state_hash: str
    goal_template_id: str | None
    steps: list[PlanStep] = field(default_factory=list)
    mode: PlannerMode = "bfs"
    success: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["steps"] = [s.to_dict() for s in self.steps]
        return d


@dataclass
class Strategy:
    name: StrategyName
    description: str
    preferred_semantics: list[str]
    priority: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
