from __future__ import annotations

from collections import Counter
from typing import Any

from asra.causality.schemas import ChangeReport
from asra.perception.transforms import TransformationDetector


def _transform_histogram(events: list[Any]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for event in events:
        tclass = getattr(event, "transform_class", None)
        if tclass is not None:
            counts[tclass.value if hasattr(tclass, "value") else str(tclass)] += 1
    return dict(counts)


class ChangeAnalyzer:
    """Unified what-changed report: cell diff + object/transform events."""

    def __init__(self) -> None:
        self.detector = TransformationDetector()

    def analyze(
        self,
        grid_before: list[list[int]],
        grid_after: list[list[int]],
        *,
        prev_hash: str | None = None,
        next_hash: str | None = None,
        level_before: str | None = None,
        level_after: str | None = None,
    ) -> ChangeReport:
        h = len(grid_before)
        w = len(grid_before[0]) if h else 0
        changed = sum(
            1 for y in range(h) for x in range(w) if grid_before[y][x] != grid_after[y][x]
        )
        detection = self.detector.detect_grids(grid_before, grid_after)
        hist = _transform_histogram(detection.events)
        scene_before = {
            "num_objects": len(detection.matches) + sum(1 for e in detection.events if e.transform_class.value == "create"),
        }
        scene_after = scene_before.copy()
        delta_objects = int(scene_after["num_objects"]) - int(scene_before["num_objects"])
        graph_edge = bool(prev_hash and next_hash and prev_hash != next_hash)
        level_changed = bool(level_before and level_after and level_before != level_after)
        summary = detection.summary
        if changed == 0 and not level_changed:
            summary = "no_change"
        return ChangeReport(
            num_changed_cells=changed,
            object_scene_before=scene_before,
            object_scene_after=scene_after,
            delta_num_objects=delta_objects,
            transform_histogram=hist,
            transform_summary=detection.summary,
            graph_edge_created=graph_edge,
            level_changed=level_changed,
            summary=summary,
        )

    def analyze_from_diff(
        self,
        diff: dict[str, Any],
        *,
        prev_hash: str | None = None,
        next_hash: str | None = None,
    ) -> ChangeReport:
        """Build ChangeReport from logged transition diff metadata."""
        hist = dict(diff.get("transform_histogram") or {})
        return ChangeReport(
            num_changed_cells=int(diff.get("num_changed_cells") or 0),
            object_scene_before=diff.get("object_scene_before"),
            object_scene_after=diff.get("object_scene_after"),
            delta_num_objects=int(diff.get("delta_num_objects") or 0),
            transform_histogram=hist,
            transform_summary=str(diff.get("transform_summary") or "unknown"),
            graph_edge_created=bool(prev_hash and next_hash and prev_hash != next_hash),
            level_changed=bool(diff.get("level_changed")),
            summary=str(diff.get("summary") or diff.get("transform_summary") or ""),
        )
