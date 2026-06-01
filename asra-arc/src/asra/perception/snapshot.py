from __future__ import annotations

import os
from typing import Any

from asra.perception.objects import ObjectExtractor
from asra.perception.regions import RegionDetector
from asra.perception.schemas import ObjectScene


def object_scenes_enabled() -> bool:
    return os.environ.get("ASRA_OBJECT_SCENES", "").strip().lower() in {"1", "true", "yes", "on"}


def scene_from_grid(grid: list[list[int]]) -> ObjectScene:
    extractor = ObjectExtractor()
    regions = RegionDetector()
    scene = extractor.extract(grid)
    return regions.annotate(grid, scene)


def compact_scene_dict(scene: ObjectScene) -> dict[str, Any]:
    """Compact representation for transition logs (no per-pixel lists)."""
    return {
        "grid_shape": list(scene.grid_shape),
        "background_color": scene.background_color,
        "num_objects": len(scene.objects),
        "objects": [
            {
                "object_id": o.object_id,
                "color": o.color,
                "area": o.area,
                "bbox": list(o.bbox),
                "shape_hash": o.shape_hash,
                "centroid": list(o.centroid),
            }
            for o in scene.objects
        ],
        "regions": [
            {
                "region_id": r.region_id,
                "region_type": r.region_type.value,
                "bbox": list(r.bbox),
            }
            for r in scene.regions
        ],
    }
