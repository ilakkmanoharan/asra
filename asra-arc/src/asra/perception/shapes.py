from __future__ import annotations

import hashlib
import json
from typing import Iterable

from asra.perception.schemas import GridObject, MatchResult, TransformClass


def _relative_pixels(pixels: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    pix = list(pixels)
    if not pix:
        return []
    min_y = min(p[0] for p in pix)
    min_x = min(p[1] for p in pix)
    return sorted((p[0] - min_y, p[1] - min_x) for p in pix)


def _rotate_90(coords: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not coords:
        return []
    max_y = max(c[0] for c in coords)
    return sorted((c[1], max_y - c[0]) for c in coords)


def _reflect_h(coords: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not coords:
        return []
    max_x = max(c[1] for c in coords)
    return sorted((c[0], max_x - c[1]) for c in coords)


def _variants(coords: list[tuple[int, int]]) -> list[list[tuple[int, int]]]:
    variants: list[list[tuple[int, int]]] = []
    current = coords
    for _ in range(4):
        variants.append(current)
        reflected = _reflect_h(current)
        variants.append(reflected)
        current = _rotate_90(current)
    return variants


def normalized_shape_signature(pixels: list[tuple[int, int]], color: int) -> str:
    rel = _relative_pixels(pixels)
    canonical = min(_variants(rel), key=lambda c: json.dumps(c))
    payload = {"color": color, "shape": canonical}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def shape_similarity(a: GridObject, b: GridObject) -> float:
    if a.shape_hash == b.shape_hash:
        return 1.0
    rel_a = _relative_pixels(a.pixels)
    rel_b = _relative_pixels(b.pixels)
    if not rel_a or not rel_b:
        return 0.0
    best = 0.0
    set_b = set(rel_b)
    for variant in _variants(rel_a):
        inter = len(set(variant) & set_b)
        union = len(set(variant) | set_b)
        if union:
            best = max(best, inter / union)
    return best


class ShapeMatcher:
    """Match objects by shape equivalence up to rotation/reflection."""

    def __init__(self, similarity_threshold: float = 0.85) -> None:
        self.similarity_threshold = similarity_threshold

    def match(self, obj_a: GridObject, obj_b: GridObject) -> MatchResult:
        sim = shape_similarity(obj_a, obj_b)
        same_hash = obj_a.shape_hash == obj_b.shape_hash
        if same_hash and obj_a.color == obj_b.color:
            tclass = TransformClass.IDENTITY
        elif same_hash and obj_a.color != obj_b.color:
            tclass = TransformClass.RECOLOR
        elif sim >= self.similarity_threshold:
            tclass = TransformClass.ROTATE if not same_hash else TransformClass.IDENTITY
        else:
            tclass = TransformClass.UNKNOWN
        return MatchResult(
            object_a_id=obj_a.object_id,
            object_b_id=obj_b.object_id,
            similarity=sim,
            transform_class=tclass,
            shape_hash_equal=same_hash,
        )

    def align(
        self,
        objects_a: list[GridObject],
        objects_b: list[GridObject],
    ) -> list[MatchResult]:
        if not objects_a or not objects_b:
            return []
        used_b: set[str] = set()
        matches: list[MatchResult] = []
        for obj_a in objects_a:
            best: MatchResult | None = None
            for obj_b in objects_b:
                if obj_b.object_id in used_b:
                    continue
                m = self.match(obj_a, obj_b)
                if best is None or m.similarity > best.similarity:
                    best = m
            if best and best.similarity >= self.similarity_threshold:
                used_b.add(best.object_b_id)
                matches.append(best)
        return matches
