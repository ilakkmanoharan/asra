from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from asra.causality.schemas import TransitionPrediction


class CausalTransitionModel:
    """Predict next-state features from (game_id, state_hash, action) — v1 lookup + averages."""

    def __init__(self) -> None:
        self._successors: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
        self._features: dict[tuple[str, str, str, str], dict[str, float]] = {}

    def observe(
        self,
        game_id: str,
        state_hash: str,
        action: str,
        next_state_hash: str,
        *,
        changed_cells: float,
        delta_num_objects: float = 0.0,
        transforms: list[str] | None = None,
    ) -> None:
        key = (game_id, state_hash, action)
        self._successors[key][next_state_hash] += 1
        feat_key = (game_id, state_hash, action, next_state_hash)
        existing = self._features.get(feat_key)
        n = 1 if existing is None else int(existing.get("_n", 0)) + 1
        prev_cells = existing.get("changed_cells", changed_cells) if existing else changed_cells
        prev_obj = existing.get("delta_num_objects", delta_num_objects) if existing else delta_num_objects
        self._features[feat_key] = {
            "changed_cells": ((prev_cells * (n - 1)) + changed_cells) / n,
            "delta_num_objects": ((prev_obj * (n - 1)) + delta_num_objects) / n,
            "transforms": transforms or [],
            "_n": float(n),
        }

    def observe_transition(self, transition: dict[str, Any]) -> None:
        game_id = str(transition.get("game_id") or "unknown")
        state = transition.get("state") or {}
        next_state = transition.get("next_state") or {}
        state_hash = str(state.get("state_hash") or "")
        next_hash = str(next_state.get("state_hash") or "")
        action = str((transition.get("action") or {}).get("name") or transition.get("action") or "")
        if not state_hash or not action or not next_hash:
            return
        diff = transition.get("diff") or {}
        meta = transition.get("metadata") or {}
        causality = meta.get("causality") or {}
        hist = causality.get("transform_histogram") or diff.get("transform_histogram") or {}
        transforms = list(hist.keys()) if isinstance(hist, dict) else []
        self.observe(
            game_id,
            state_hash,
            action,
            next_hash,
            changed_cells=float(diff.get("num_changed_cells") or 0),
            delta_num_objects=float(diff.get("delta_num_objects") or 0),
            transforms=transforms,
        )

    def predict(self, game_id: str, state_hash: str, action: str) -> TransitionPrediction:
        key = (game_id, state_hash, action)
        counts = self._successors.get(key)
        if not counts:
            return TransitionPrediction(
                predicted_next_hash=None,
                predicted_changed_cells=0.0,
                predicted_object_delta=0.0,
                predicted_transforms=[],
                probability=0.0,
                support_count=0,
            )
        total = sum(counts.values())
        next_hash, top_count = counts.most_common(1)[0]
        feat = self._features.get((game_id, state_hash, action, next_hash), {})
        return TransitionPrediction(
            predicted_next_hash=next_hash,
            predicted_changed_cells=float(feat.get("changed_cells", 0.0)),
            predicted_object_delta=float(feat.get("delta_num_objects", 0.0)),
            predicted_transforms=list(feat.get("transforms") or []),
            probability=top_count / total,
            support_count=total,
        )

    def global_mean_changed_cells(self) -> float:
        vals = [float(f.get("changed_cells", 0.0)) for f in self._features.values()]
        return sum(vals) / len(vals) if vals else 0.0
