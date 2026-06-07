from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

GoalStatus = Literal["active", "leading", "confirmed", "refuted", "weak"]
ObjectRoleName = Literal[
    "agent", "target", "token", "hazard", "key", "door", "decoration", "unknown"
]
ProgressSignalType = Literal[
    "reward", "level_up", "win", "object_progress", "pattern_progress", "token_progress"
]


@dataclass
class GoalHypothesis:
    hypothesis_id: str
    game_id: str
    template_id: str
    description: str
    preferred_semantics: list[str] = field(default_factory=list)
    progress_weights: dict[str, float] = field(default_factory=dict)
    object_roles: dict[str, str] = field(default_factory=dict)
    preconditions: dict[str, Any] = field(default_factory=dict)
    support: int = 0
    refute: int = 0
    progress_score: float = 0.0
    status: GoalStatus = "active"
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProgressSignal:
    signal_id: str
    episode_id: str
    step: int
    signal_type: ProgressSignalType
    magnitude: float
    state_hash: str
    action: str
    semantic_label: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ObjectRole:
    object_id: str
    role: ObjectRoleName
    confidence: float
    features: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExperimentPlan:
    plan_id: str
    state_hash: str
    candidate_actions: list[str]
    target_hypotheses: list[str]
    discrimination_scores: dict[str, float]
    chosen_action: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
