from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class RegionType(str, Enum):
    BACKGROUND = "BACKGROUND"
    FRAME = "FRAME"
    CONTENT_BBOX = "CONTENT_BBOX"


class TransformClass(str, Enum):
    IDENTITY = "IDENTITY"
    RECOLOR = "RECOLOR"
    TRANSLATE = "TRANSLATE"
    ROTATE = "ROTATE"
    REFLECT = "REFLECT"
    CREATE = "CREATE"
    DELETE = "DELETE"
    COMPOSE = "COMPOSE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class GridObject:
    object_id: str
    color: int
    pixels: tuple[tuple[int, int], ...]
    bbox: tuple[int, int, int, int]
    area: int
    shape_hash: str
    centroid: tuple[float, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "color": self.color,
            "pixels": [list(p) for p in self.pixels],
            "bbox": list(self.bbox),
            "area": self.area,
            "shape_hash": self.shape_hash,
            "centroid": list(self.centroid),
        }


@dataclass
class Region:
    region_id: str
    region_type: RegionType
    color: int | None
    bbox: tuple[int, int, int, int]
    area: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "region_id": self.region_id,
            "region_type": self.region_type.value,
            "color": self.color,
            "bbox": list(self.bbox),
            "area": self.area,
        }


@dataclass
class ObjectScene:
    grid_shape: tuple[int, int]
    background_color: int
    objects: list[GridObject] = field(default_factory=list)
    regions: list[Region] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "grid_shape": list(self.grid_shape),
            "background_color": self.background_color,
            "objects": [o.to_dict() for o in self.objects],
            "regions": [r.to_dict() for r in self.regions],
        }


@dataclass(frozen=True)
class MatchResult:
    object_a_id: str
    object_b_id: str
    similarity: float
    transform_class: TransformClass
    shape_hash_equal: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "object_a_id": self.object_a_id,
            "object_b_id": self.object_b_id,
            "similarity": self.similarity,
            "transform_class": self.transform_class.value,
            "shape_hash_equal": self.shape_hash_equal,
        }


@dataclass
class TransformEvent:
    transform_class: TransformClass
    object_id_before: str | None = None
    object_id_after: str | None = None
    color_before: int | None = None
    color_after: int | None = None
    delta_centroid: tuple[float, float] | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["transform_class"] = self.transform_class.value
        return d


@dataclass
class TransformDetection:
    events: list[TransformEvent] = field(default_factory=list)
    matches: list[MatchResult] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "events": [e.to_dict() for e in self.events],
            "matches": [m.to_dict() for m in self.matches],
            "summary": self.summary,
        }


@dataclass
class RuleCandidate:
    rule_id: str
    pattern: str
    support: int
    confidence: float
    transform_types: list[str] = field(default_factory=list)
    rule_scope: str = "global"
    demo_index: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
