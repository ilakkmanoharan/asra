"""ASRA Phase 2 agent — Kaggle template form (auto-extracted).

Spliced into submission notebook. Must expose class MyAgent.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

# --- compact object perception (embedded; mirrors asra_phase2_compact_perception.py) ---


def _dominant_background(grid: List[List[int]]) -> int:
    counts: Counter[int] = Counter()
    for row in grid:
        counts.update(row)
    return counts.most_common(1)[0][0] if counts else 0


def _connected_components(
    grid: List[List[int]], background: int, connectivity: int = 4
) -> List[Tuple[int, List[Tuple[int, int]]]]:
    h = len(grid)
    w = len(grid[0]) if h else 0
    visited = [[False] * w for _ in range(h)]
    components: List[Tuple[int, List[Tuple[int, int]]]] = []
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)] if connectivity == 4 else [
        (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]
    for y in range(h):
        for x in range(w):
            color = grid[y][x]
            if color == background or visited[y][x]:
                continue
            stack = [(y, x)]
            visited[y][x] = True
            pixels: List[Tuple[int, int]] = []
            while stack:
                cy, cx = stack.pop()
                pixels.append((cy, cx))
                for dy, dx in neighbors:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and not visited[ny][nx] and grid[ny][nx] == color:
                        visited[ny][nx] = True
                        stack.append((ny, nx))
            components.append((color, pixels))
    return components


def compact_scene(grid: List[List[int]]) -> Dict[str, Any]:
    if not grid or not grid[0]:
        return {"grid_shape": [0, 0], "background_color": 0, "num_objects": 0, "objects": []}
    bg = _dominant_background(grid)
    objects = []
    for idx, (color, pixels) in enumerate(_connected_components(grid, bg)):
        if not pixels:
            continue
        ys = [p[0] for p in pixels]
        xs = [p[1] for p in pixels]
        bbox = [min(ys), min(xs), max(ys), max(xs)]
        n = len(pixels)
        cy = sum(ys) / n
        cx = sum(xs) / n
        objects.append(
            {"object_id": f"obj_{idx}", "color": int(color), "area": n, "bbox": bbox, "centroid": [cy, cx]}
        )
    return {
        "grid_shape": [len(grid), len(grid[0])],
        "background_color": int(bg),
        "num_objects": len(objects),
        "objects": objects,
    }


def object_delta(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "delta_num_objects": int(after.get("num_objects", 0)) - int(before.get("num_objects", 0)),
        "before_num_objects": int(before.get("num_objects", 0)),
        "after_num_objects": int(after.get("num_objects", 0)),
    }


import numpy as np
from agents.agent import Agent
from arcengine import FrameData, GameAction, GameState


SEED = int(os.environ.get("ASRA_SEED", "42"))
MAX_ACTIONS = int(os.environ.get("ASRA_MAX_ACTIONS", "80"))
SIMPLE_ACTIONS = ["ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION5", "ACTION7"]
OBJECT_HINT_WEIGHT = float(os.environ.get("ASRA_OBJECT_HINT_WEIGHT", "0.35"))

random.seed(SEED)
np.random.seed(SEED)


def canonical_grid(grid: Any) -> List[List[int]]:
    return np.array(grid, dtype=int).tolist()


def state_hash(grid: Any) -> str:
    payload = json.dumps(canonical_grid(grid), separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ActionSemanticsInferencer:
    def __init__(self) -> None:
        self.effects: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)

    def observe(self, state_hash_value: str, action: str, diff: Dict[str, Any], reward: float) -> None:
        self.effects[(state_hash_value, action)].append(
            {
                "num_changed_cells": diff.get("num_changed_cells"),
                "reward": reward,
                "delta_num_objects": diff.get("delta_num_objects"),
            }
        )

    def infer(self, state_hash_value: str, action: str) -> Dict[str, Any]:
        effects = self.effects.get((state_hash_value, action), [])
        if not effects:
            return {"observations": 0, "hypothesis": "unknown", "consistency_score": None}
        counts = [e["num_changed_cells"] for e in effects if e["num_changed_cells"] is not None]
        obj_deltas = [e.get("delta_num_objects") for e in effects if e.get("delta_num_objects") is not None]
        std = float(np.std(counts)) if counts else 0.0
        mean = float(np.mean(counts)) if counts else None
        if mean == 0:
            hyp = "no-op / blocked"
        elif mean is not None and mean <= 1.5:
            hyp = "localized cell update"
        else:
            hyp = "multi-cell transform"
        obj_mean = float(np.mean(obj_deltas)) if obj_deltas else 0.0
        return {
            "observations": len(effects),
            "hypothesis": hyp,
            "consistency_score": float(1.0 / (1.0 + std)) if counts else None,
            "mean_delta_objects": obj_mean,
        }


class ASRAExplorer:
    def __init__(self, action_names: List[str]) -> None:
        self.action_names = action_names
        self.state_action_counts: Counter = Counter()
        self.action_rewards: Dict[str, List[float]] = defaultdict(list)
        self.object_effect_scores: Dict[Tuple[str, str], float] = defaultdict(float)
        self.dead_ends: set = set()

    def update(self, state_hash_value: str, action: str, diff: Dict[str, Any], reward: float) -> None:
        self.state_action_counts[(state_hash_value, action)] += 1
        self.action_rewards[action].append(float(reward))
        if diff.get("num_changed_cells") == 0 and reward <= 0:
            self.dead_ends.add((state_hash_value, action))
        delta_obj = diff.get("delta_num_objects")
        if delta_obj is not None and delta_obj != 0:
            key = (state_hash_value, action)
            self.object_effect_scores[key] += 0.5 * (1.0 if delta_obj > 0 else 0.7)

    def choose_action(
        self,
        state_hash_value: str,
        semantics: ActionSemanticsInferencer,
        available: Optional[List[str]] = None,
        scene_hint: Optional[Dict[str, Any]] = None,
    ) -> str:
        candidates = [a for a in self.action_names if available is None or a in available] or list(self.action_names)
        scores: Dict[str, float] = {}
        num_objects = int((scene_hint or {}).get("num_objects", 0))
        for action in candidates:
            if (state_hash_value, action) in self.dead_ends:
                continue
            sem = semantics.infer(state_hash_value, action)
            c = sem.get("consistency_score")
            uncertainty = 1.0 if c is None else (1.0 - min(1.0, c))
            local = self.state_action_counts[(state_hash_value, action)]
            mean_r = float(np.mean(self.action_rewards[action])) if self.action_rewards[action] else 0.0
            obj_bonus = OBJECT_HINT_WEIGHT * self.object_effect_scores.get((state_hash_value, action), 0.0)
            if num_objects == 0:
                obj_bonus *= 0.5
            scores[action] = (
                2.0 / (1.0 + local) + 0.7 * uncertainty + 0.5 * mean_r + obj_bonus + random.random() * 0.05
            )
        return max(scores.items(), key=lambda kv: kv[1])[0] if scores else random.choice(candidates)


GLOBAL_SEMANTICS = ActionSemanticsInferencer()
GLOBAL_EXPLORER = ASRAExplorer(SIMPLE_ACTIONS)


class MyAgent(Agent):
    """Phase 2: transition logging + compact object-scene hints for exploration."""

    MAX_ACTIONS = MAX_ACTIONS

    def is_done(self, frames: List[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state is GameState.WIN or self.action_counter >= self.MAX_ACTIONS

    def _available_simple(self, latest_frame: FrameData) -> List[str]:
        avail = getattr(latest_frame, "available_actions", None) or []
        names = [a.name for a in avail if hasattr(a, "name") and a.name in SIMPLE_ACTIONS]
        return names or SIMPLE_ACTIONS

    def _to_game_action(self, action_name: str, grid: Any, scene_hint: Optional[Dict[str, Any]] = None) -> GameAction:
        ga = getattr(GameAction, action_name)
        if ga.is_complex():
            h, w = len(grid), len(grid[0]) if grid else 0
            ga.set_data({"x": w // 2, "y": h // 2})
        n_obj = (scene_hint or {}).get("num_objects", "?")
        ga.reasoning = f"ASRA Phase2: {action_name} | objects={n_obj}"
        return ga

    def choose_action(self, frames: List[FrameData], latest_frame: FrameData) -> GameAction:
        if latest_frame.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            return GameAction.RESET
        grid = latest_frame.frame
        scene = compact_scene(canonical_grid(grid))
        name = GLOBAL_EXPLORER.choose_action(
            state_hash(grid), GLOBAL_SEMANTICS, self._available_simple(latest_frame), scene_hint=scene
        )
        return self._to_game_action(name, grid, scene)

    def take_action(self, action: GameAction) -> Optional[FrameData]:
        self._last_action_name = action.name
        return super().take_action(action)

    def append_frame(self, frame: FrameData) -> None:
        super().append_frame(frame)
        if len(self.frames) < 2:
            return
        prev, curr = self.frames[-2], self.frames[-1]
        if not prev.frame or not curr.frame:
            return
        prev_grid = canonical_grid(prev.frame)
        curr_grid = canonical_grid(curr.frame)
        diff_count = int(np.sum(np.array(prev_grid) != np.array(curr_grid)))
        scene_before = compact_scene(prev_grid)
        scene_after = compact_scene(curr_grid)
        diff = {
            "num_changed_cells": diff_count,
            "object_scene_before": scene_before,
            "object_scene_after": scene_after,
            **object_delta(scene_before, scene_after),
        }
        reward = float(getattr(curr, "levels_completed", 0) or 0)
        sh = state_hash(prev_grid)
        action = getattr(self, "_last_action_name", "UNKNOWN")
        GLOBAL_SEMANTICS.observe(sh, action, diff, reward)
        GLOBAL_EXPLORER.update(sh, action, diff, reward)
