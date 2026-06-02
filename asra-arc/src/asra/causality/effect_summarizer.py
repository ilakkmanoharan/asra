from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from typing import Any

from asra.agent.action_tester import classify_effect
from asra.causality.schemas import ActionEffectSignature


def _semantic_label(
    mean_cells: float,
    object_delta_mean: float,
    transform_histogram: dict[str, int],
    terminal_rate: float,
    dead_end_rate: float,
) -> str:
    if terminal_rate >= 0.5:
        return "terminal_transition"
    if dead_end_rate >= 0.5:
        return "dead_end"
    if mean_cells == 0 and object_delta_mean == 0:
        return "no_op"
    top_transform = max(transform_histogram, key=transform_histogram.get) if transform_histogram else None
    if top_transform in {"translate", "TRANSLATE"}:
        return "translate"
    if top_transform in {"recolor", "RECOLOR"}:
        return "recolor"
    if top_transform in {"create", "CREATE"}:
        return "create_object"
    if top_transform in {"delete", "DELETE"}:
        return "delete_object"
    if top_transform in {"rotate", "ROTATE"}:
        return "rotate"
    if mean_cells <= 1.5:
        return "localized_transform"
    if object_delta_mean != 0:
        return "object_count_change"
    return "multi_cell_transform"


class ActionEffectSummarizer:
    """Aggregate (game, state, action) observations into effect signatures."""

    def __init__(self) -> None:
        self._observations: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)

    def observe(
        self,
        game_id: str,
        state_hash: str,
        action: str,
        *,
        changed_cells: int,
        delta_num_objects: float = 0.0,
        transform_histogram: dict[str, int] | None = None,
        terminal: bool = False,
        dead_end: bool = False,
        next_state_hash: str | None = None,
    ) -> None:
        self._observations[(game_id, state_hash, action)].append(
            {
                "changed_cells": changed_cells,
                "delta_num_objects": delta_num_objects,
                "transform_histogram": dict(transform_histogram or {}),
                "terminal": terminal,
                "dead_end": dead_end,
                "next_state_hash": next_state_hash,
            }
        )

    def observe_transition(self, transition: dict[str, Any]) -> None:
        game_id = str(transition.get("game_id") or "unknown")
        state = transition.get("state") or {}
        state_hash = str(state.get("state_hash") or "")
        action = str((transition.get("action") or {}).get("name") or transition.get("action") or "")
        if not state_hash or not action:
            return
        diff = transition.get("diff") or {}
        meta = transition.get("metadata") or {}
        causality = meta.get("causality") or {}
        hist = causality.get("transform_histogram") or diff.get("transform_histogram") or {}
        terminal = bool(transition.get("terminal_state"))
        dead_end = float(meta.get("dead_end_score") or 0.0) >= 0.8
        next_state = transition.get("next_state") or {}
        self.observe(
            game_id,
            state_hash,
            action,
            changed_cells=int(diff.get("num_changed_cells") or 0),
            delta_num_objects=float(diff.get("delta_num_objects") or causality.get("delta_num_objects") or 0),
            transform_histogram=hist if isinstance(hist, dict) else {},
            terminal=terminal,
            dead_end=dead_end,
            next_state_hash=str(next_state.get("state_hash") or ""),
        )

    def summarize(self, game_id: str, state_hash: str, action: str) -> ActionEffectSignature:
        obs = self._observations.get((game_id, state_hash, action), [])
        if not obs:
            return ActionEffectSignature(
                action=action,
                game_id=game_id,
                state_hash=state_hash,
                semantic_label="unknown",
                confidence=0.0,
            )
        cells = [float(o["changed_cells"]) for o in obs]
        obj_deltas = [float(o["delta_num_objects"]) for o in obs]
        mean_cells = sum(cells) / len(cells)
        std_cells = math.sqrt(sum((c - mean_cells) ** 2 for c in cells) / len(cells)) if len(cells) > 1 else 0.0
        mean_obj = sum(obj_deltas) / len(obj_deltas)
        hist: Counter[str] = Counter()
        for o in obs:
            hist.update(o.get("transform_histogram") or {})
        terminal_rate = sum(1 for o in obs if o["terminal"]) / len(obs)
        dead_end_rate = sum(1 for o in obs if o["dead_end"]) / len(obs)
        label = _semantic_label(mean_cells, mean_obj, dict(hist), terminal_rate, dead_end_rate)
        consistency = 1.0 / (1.0 + std_cells)
        confidence = min(1.0, (len(obs) / 5.0) * 0.6 + consistency * 0.4)
        sig_id = hashlib.sha256(
            json.dumps(
                {"game_id": game_id, "state_hash": state_hash, "action": action, "label": label},
                sort_keys=True,
            ).encode()
        ).hexdigest()[:12]
        return ActionEffectSignature(
            action=action,
            game_id=game_id,
            state_hash=state_hash,
            observation_count=len(obs),
            cell_change_mean=mean_cells,
            cell_change_std=std_cells,
            object_delta_mean=mean_obj,
            transform_histogram=dict(hist),
            terminal_rate=terminal_rate,
            dead_end_rate=dead_end_rate,
            semantic_label=label,
            confidence=confidence,
            signature_id=sig_id,
        )

    def summarize_all(self) -> list[ActionEffectSignature]:
        keys = sorted(self._observations.keys())
        return [self.summarize(g, s, a) for g, s, a in keys]

    def legacy_effect_type(self, signature: ActionEffectSignature, total_cells: int = 100) -> str:
        return classify_effect(
            int(round(signature.cell_change_mean)),
            total_cells,
            signature.terminal_rate >= 0.5,
            False,
            signature.dead_end_rate >= 0.5,
        )
