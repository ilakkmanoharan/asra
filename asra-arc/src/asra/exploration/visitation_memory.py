from __future__ import annotations

from collections import deque
from typing import Any


class VisitationMemory:
    """Per-episode and cross-episode visit tracking at hash and object-fingerprint resolution."""

    def __init__(self, recent_window: int = 20) -> None:
        self._window_size = recent_window
        self._visit_counts: dict[str, int] = {}
        self._object_fingerprints: dict[str, int] = {}
        self._recent: deque[str] = deque(maxlen=recent_window)
        self._step = 0

    def observe(self, state_hash: str, step: int | None = None, object_scene: dict[str, Any] | None = None) -> None:
        self._step = step if step is not None else self._step + 1
        self._visit_counts[state_hash] = self._visit_counts.get(state_hash, 0) + 1
        self._recent.append(state_hash)
        if object_scene:
            fp = object_scene_fingerprint(object_scene)
            self._object_fingerprints[fp] = self._object_fingerprints.get(fp, 0) + 1

    def visit_count(self, state_hash: str) -> int:
        return self._visit_counts.get(state_hash, 0)

    def is_novel(self, state_hash: str) -> bool:
        return self.visit_count(state_hash) <= 1

    def object_fingerprint_seen(self, object_scene: dict[str, Any]) -> int:
        return self._object_fingerprints.get(object_scene_fingerprint(object_scene), 0)

    def recent_window(self, n: int | None = None) -> list[str]:
        n = n or self._window_size
        return list(self._recent)[-n:]

    def count_in_recent(self, state_hash: str) -> int:
        return self.recent_window().count(state_hash)


def object_scene_fingerprint(object_scene: dict[str, Any]) -> str:
    """Compact key from object counts and shape hashes (Phase 2 compact scenes)."""
    import hashlib
    import json

    objs = object_scene.get("objects") or []
    payload = {
        "num_objects": object_scene.get("num_objects", len(objs)),
        "signatures": sorted((o.get("color"), o.get("area"), tuple(o.get("bbox", []))) for o in objs),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]
