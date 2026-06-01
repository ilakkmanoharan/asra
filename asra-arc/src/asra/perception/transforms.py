from __future__ import annotations

from asra.perception.objects import ObjectExtractor
from asra.perception.regions import RegionDetector
from asra.perception.schemas import ObjectScene, TransformClass, TransformDetection, TransformEvent
from asra.perception.shapes import ShapeMatcher


class TransformationDetector:
    """Classify object-level changes between two grids or scenes."""

    def __init__(self) -> None:
        self.extractor = ObjectExtractor()
        self.regions = RegionDetector()
        self.matcher = ShapeMatcher()

    def detect_scenes(self, before: ObjectScene, after: ObjectScene) -> TransformDetection:
        matches = self.matcher.align(before.objects, after.objects)
        matched_after = {m.object_b_id for m in matches}
        matched_before = {m.object_a_id for m in matches}
        events: list[TransformEvent] = []

        for m in matches:
            obj_a = next(o for o in before.objects if o.object_id == m.object_a_id)
            obj_b = next(o for o in after.objects if o.object_id == m.object_b_id)
            dy = obj_b.centroid[0] - obj_a.centroid[0]
            dx = obj_b.centroid[1] - obj_a.centroid[1]
            tclass = m.transform_class
            if abs(dy) > 0.4 or abs(dx) > 0.4:
                if tclass == TransformClass.IDENTITY:
                    tclass = TransformClass.TRANSLATE
            events.append(
                TransformEvent(
                    transform_class=tclass,
                    object_id_before=obj_a.object_id,
                    object_id_after=obj_b.object_id,
                    color_before=obj_a.color,
                    color_after=obj_b.color,
                    delta_centroid=(dy, dx),
                    details={"similarity": m.similarity},
                )
            )

        for obj in before.objects:
            if obj.object_id not in matched_before:
                events.append(
                    TransformEvent(
                        transform_class=TransformClass.DELETE,
                        object_id_before=obj.object_id,
                        color_before=obj.color,
                    )
                )
        for obj in after.objects:
            if obj.object_id not in matched_after:
                events.append(
                    TransformEvent(
                        transform_class=TransformClass.CREATE,
                        object_id_after=obj.object_id,
                        color_after=obj.color,
                    )
                )

        if len(events) > 1:
            summary = f"{len(events)} events: " + ", ".join(sorted({e.transform_class.value for e in events}))
        elif events:
            summary = events[0].transform_class.value
        else:
            summary = TransformClass.IDENTITY.value

        return TransformDetection(events=events, matches=matches, summary=summary)

    def detect_grids(self, grid_before: list[list[int]], grid_after: list[list[int]]) -> TransformDetection:
        scene_before = self.regions.annotate(grid_before, self.extractor.extract(grid_before))
        scene_after = self.regions.annotate(grid_after, self.extractor.extract(grid_after))
        return self.detect_scenes(scene_before, scene_after)
