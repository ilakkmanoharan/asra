from __future__ import annotations

from typing import Any

from asra.goals.schemas import ObjectRole


class ObjectRoleClassifier:
    """Heuristic object role labels from compact scenes (Phase 2)."""

    def classify(self, scene: dict[str, Any]) -> list[ObjectRole]:
        objects = scene.get("objects") or []
        if not objects:
            return []
        areas = [int(o.get("area", 0)) for o in objects]
        max_area = max(areas) if areas else 0
        roles: list[ObjectRole] = []
        area_counts: dict[int, int] = {}
        for o in objects:
            area_counts[int(o.get("area", 0))] = area_counts.get(int(o.get("area", 0)), 0) + 1

        for obj in objects:
            oid = str(obj.get("object_id", "unknown"))
            area = int(obj.get("area", 0))
            color = int(obj.get("color", 0))
            role = "unknown"
            confidence = 0.4
            if area == max_area and len(objects) <= 4:
                role = "agent"
                confidence = 0.55
            elif area_counts.get(area, 0) >= 3 and area <= max_area * 0.3:
                role = "token"
                confidence = 0.6
            elif color in (2, 3, 8) and area < max_area * 0.5:
                role = "hazard"
                confidence = 0.45
            elif area < max_area * 0.25:
                role = "key"
                confidence = 0.4
            else:
                role = "target"
                confidence = 0.5
            roles.append(
                ObjectRole(
                    object_id=oid,
                    role=role,  # type: ignore[arg-type]
                    confidence=confidence,
                    features={"area": area, "color": color, "bbox": obj.get("bbox")},
                )
            )
        return roles

    def roles_dict(self, scene: dict[str, Any]) -> dict[str, str]:
        return {r.object_id: r.role for r in self.classify(scene)}
