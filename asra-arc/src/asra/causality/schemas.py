from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


HypothesisStatus = Literal["active", "confirmed", "refuted", "weak"]


@dataclass
class ChangeReport:
    num_changed_cells: int
    object_scene_before: dict[str, Any] | None = None
    object_scene_after: dict[str, Any] | None = None
    delta_num_objects: int = 0
    transform_histogram: dict[str, int] = field(default_factory=dict)
    transform_summary: str = "identity"
    graph_edge_created: bool = False
    level_changed: bool = False
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ActionEffectSignature:
    action: str
    game_id: str
    state_hash: str
    observation_count: int = 0
    cell_change_mean: float = 0.0
    cell_change_std: float = 0.0
    object_delta_mean: float = 0.0
    transform_histogram: dict[str, int] = field(default_factory=dict)
    terminal_rate: float = 0.0
    dead_end_rate: float = 0.0
    semantic_label: str = "unknown"
    confidence: float = 0.0
    signature_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TransitionPrediction:
    predicted_next_hash: str | None
    predicted_changed_cells: float
    predicted_object_delta: float
    predicted_transforms: list[str]
    probability: float
    support_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CausalHypothesis:
    hypothesis_id: str
    game_id: str
    action: str
    predicted_effect: str
    precondition: dict[str, Any] = field(default_factory=dict)
    support: int = 0
    refute: int = 0
    status: HypothesisStatus = "active"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CounterfactualResult:
    state_hash: str
    actual_action: str
    alt_action: str
    predicted_changed_cells: float
    predicted_object_delta: float
    predicted_transforms: list[str]
    confidence: float
    source: Literal["observed", "model", "none"]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
