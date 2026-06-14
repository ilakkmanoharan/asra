from agents.agent import Agent
"""ASRA Phase 7 agent — Kaggle template form (auto-extracted).

Spliced into submission notebook. Must expose class MyAgent.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
from collections import Counter, defaultdict, deque
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# --- Phase 3 compact exploration hints (embedded) ---


class CompactExplorationHints:
    """Visit memory + frontier bonus for action scoring."""

    def __init__(self, recent_window: int = 20) -> None:
        self.visit_counts: Dict[str, int] = defaultdict(int)
        self.recent: deque[str] = deque(maxlen=recent_window)
        self.edge_stats: Dict[Tuple[str, str], Dict[str, float]] = defaultdict(
            lambda: {"novelty": 0.0, "usefulness": 0.0, "n": 0.0}
        )

    def observe(self, state_hash: str, next_hash: str, action: str, reward: float, changed_cells: int) -> None:
        self.visit_counts[state_hash] += 1
        self.visit_counts[next_hash] += 1
        self.recent.append(next_hash)
        novelty = 1.0 / (1.0 + self.visit_counts[next_hash]) ** 0.5
        usefulness = float(reward) + (0.5 if changed_cells else 0.0)
        key = (state_hash, action)
        stats = self.edge_stats[key]
        stats["n"] += 1
        stats["novelty"] = ((stats["novelty"] * (stats["n"] - 1)) + novelty) / stats["n"]
        stats["usefulness"] = ((stats["usefulness"] * (stats["n"] - 1)) + usefulness) / stats["n"]

    def score_action(self, state_hash: str, action: str) -> float:
        visits = self.visit_counts[state_hash]
        frontier_bonus = 1.0 / (1.0 + visits) ** 0.5
        stats = self.edge_stats.get((state_hash, action))
        if stats and stats["n"] > 0:
            repeat_penalty = 1.0 if self.recent.count(state_hash) > 2 else 0.0
            return stats["novelty"] + stats["usefulness"] + frontier_bonus - repeat_penalty
        return frontier_bonus + 0.5

    def exploration_metadata(self, state_hash: str) -> Dict[str, Any]:
        return {
            "visit_count_before": self.visit_counts[state_hash],
            "frontier_node": self.visit_counts[state_hash] <= 2,
            "recent_unique": len(set(self.recent)),
        }


# --- Phase 2 compact object perception (embedded) ---


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
        objects.append(
            {
                "object_id": f"obj_{idx}",
                "color": int(color),
                "area": n,
                "bbox": bbox,
                "centroid": [sum(ys) / n, sum(xs) / n],
            }
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


def transform_histogram_from_scenes(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, int]:
    """Lightweight transform tags from object-scene deltas (Phase 4 embedded)."""
    hist: Counter = Counter()
    delta = int(after.get("num_objects", 0)) - int(before.get("num_objects", 0))
    if delta > 0:
        hist["create"] += delta
    elif delta < 0:
        hist["delete"] += -delta
    before_objs = {o["object_id"]: o for o in before.get("objects", [])}
    after_objs = {o["object_id"]: o for o in after.get("objects", [])}
    for oid, obj_b in before_objs.items():
        obj_a = after_objs.get(oid)
        if obj_a is None:
            continue
        if obj_b.get("color") != obj_a.get("color"):
            hist["recolor"] += 1
        cy0, cx0 = obj_b.get("centroid", [0, 0])
        cy1, cx1 = obj_a.get("centroid", [0, 0])
        if abs(cy1 - cy0) > 0.4 or abs(cx1 - cx0) > 0.4:
            hist["translate"] += 1
    if not hist and before.get("num_objects") == after.get("num_objects"):
        hist["identity"] = 1
    return dict(hist)


SEED = int(os.environ.get("ASRA_SEED", "42"))
MAX_ACTIONS = int(os.environ.get("ASRA_MAX_ACTIONS", "80"))
SIMPLE_ACTIONS = ["ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION5", "ACTION7"]
OBJECT_HINT_WEIGHT = float(os.environ.get("ASRA_OBJECT_HINT_WEIGHT", "0.30"))
EXPLORATION_HINT_WEIGHT = float(os.environ.get("ASRA_EXPLORATION_HINT_WEIGHT", "0.35"))
SEMANTICS_HINT_WEIGHT = float(os.environ.get("ASRA_SEMANTICS_HINT_WEIGHT", "0.35"))
PREDICTION_HINT_WEIGHT = float(os.environ.get("ASRA_PREDICTION_HINT_WEIGHT", "0.20"))
UNCERTAINTY_HINT_WEIGHT = float(os.environ.get("ASRA_UNCERTAINTY_HINT_WEIGHT", "0.30"))
GOAL_HINT_WEIGHT = float(os.environ.get("ASRA_GOAL_HINT_WEIGHT", "0.25"))
EXPERIMENT_HINT_WEIGHT = float(os.environ.get("ASRA_EXPERIMENT_HINT_WEIGHT", "0.15"))
ROBUST_HINT_WEIGHT = float(os.environ.get("ASRA_ROBUST_HINT_WEIGHT", "-0.25"))
PLAN_HINT_WEIGHT = float(os.environ.get("ASRA_PLAN_HINT_WEIGHT", "0.20"))

random.seed(SEED)
np.random.seed(SEED)


def canonical_grid(grid: Any) -> List[List[int]]:
    return np.array(grid, dtype=int).tolist()


def state_hash(grid: Any) -> str:
    payload = json.dumps(canonical_grid(grid), separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ASRAExplorer:
    """Phase 2 object hints + Phase 3 exploration + Phase 4 causality + Phase 7 goals."""

    def __init__(self, action_names: List[str]) -> None:
        self.action_names = action_names
        self.state_action_counts: Counter = Counter()
        self.action_rewards: Dict[str, List[float]] = defaultdict(list)
        self.object_effect_scores: Dict[Tuple[str, str], float] = defaultdict(float)
        self.dead_ends: set = set()
        self.exploration = CompactExplorationHints()
        self.goals = GoalHypothesisEngine()
        self.robust = RobustnessEngine()
        self.planning = PlanningEngine()
        self._last_level: int = 0

    def update(
        self,
        state_hash_value: str,
        next_hash: str,
        action: str,
        diff: Dict[str, Any],
        reward: float,
        *,
        semantics: Optional[Dict[str, Any]] = None,
        level_completed: int = 0,
    ) -> None:
        self.state_action_counts[(state_hash_value, action)] += 1
        self.action_rewards[action].append(float(reward))
        changed = int(diff.get("num_changed_cells") or 0)
        if changed == 0 and reward <= 0:
            self.dead_ends.add((state_hash_value, action))
        delta_obj = diff.get("delta_num_objects")
        if delta_obj is not None and delta_obj != 0:
            self.object_effect_scores[(state_hash_value, action)] += 0.5 * (1.0 if delta_obj > 0 else 0.7)
        self.exploration.observe(state_hash_value, next_hash, action, reward, changed)
        self.robust.observe(state_hash_value, changed, float(reward))
        self.planning.observe(state_hash_value, action, next_hash)
        level_delta = max(0, int(level_completed) - self._last_level)
        self._last_level = max(self._last_level, int(level_completed))
        if semantics:
            self.goals.observe_progress(
                reward=float(reward),
                level_delta=level_delta,
                semantics=semantics,
                diff=diff,
            )

    def choose_action(
        self,
        state_hash_value: str,
        semantics: CausalSemanticsEngine,
        available: Optional[List[str]] = None,
        scene_hint: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        if scene_hint:
            self.goals.ensure_hypotheses(scene_hint)
        candidates = [a for a in self.action_names if available is None or a in available] or list(self.action_names)
        scores: Dict[str, float] = {}
        meta_by_action: Dict[str, Dict[str, Any]] = {}
        num_objects = int((scene_hint or {}).get("num_objects", 0))
        for action in candidates:
            if (state_hash_value, action) in self.dead_ends:
                continue
            sem = semantics.infer(state_hash_value, action)
            uncertainty = float(sem.get("uncertainty") or 1.0)
            confidence = float(sem.get("confidence") or 0.0)
            predicted = float(sem.get("predicted_changed_cells") or 0.0)
            local = self.state_action_counts[(state_hash_value, action)]
            mean_r = float(np.mean(self.action_rewards[action])) if self.action_rewards[action] else 0.0
            obj_bonus = OBJECT_HINT_WEIGHT * self.object_effect_scores.get((state_hash_value, action), 0.0)
            if num_objects == 0:
                obj_bonus *= 0.5
            explore_bonus = EXPLORATION_HINT_WEIGHT * self.exploration.score_action(state_hash_value, action)
            sem_bonus = SEMANTICS_HINT_WEIGHT * confidence
            pred_bonus = PREDICTION_HINT_WEIGHT * min(1.0, predicted / 10.0)
            unc_bonus = UNCERTAINTY_HINT_WEIGHT * uncertainty
            goal_bonus = GOAL_HINT_WEIGHT * self.goals.action_goal_score(sem)
            plan_bonus = PLAN_HINT_WEIGHT * self.planning.plan_bonus(state_hash_value, action, (lead or {}).get('template_id'), self.exploration.visit_counts[state_hash_value])
            stuck_pen = ROBUST_HINT_WEIGHT * (self.robust.stuck_penalty(state_hash_value) + self.robust.action_waste_penalty(action, local))
            exp_bonus = EXPERIMENT_HINT_WEIGHT * self.goals.experiment_discrimination_bonus(
                state_hash_value, action, semantics
            )
            scores[action] = (
                2.0 / (1.0 + local)
                + unc_bonus
                + sem_bonus
                + pred_bonus
                + goal_bonus
                + exp_bonus
                + 0.5 * mean_r
                + obj_bonus
                + explore_bonus
                + plan_bonus
                + random.random() * 0.05
            )
            meta_by_action[action] = sem
        if not scores:
            action = random.choice(candidates)
            lead = self.goals.leading_hypothesis() or {}
            return action, meta_by_action.get(action, {}), lead
        action = max(scores.items(), key=lambda kv: kv[1])[0]
        lead = self.goals.leading_hypothesis() or {}
        return action, meta_by_action.get(action, {}), lead


GLOBAL_SEMANTICS = CausalSemanticsEngine()
GLOBAL_EXPLORER = ASRAExplorer(SIMPLE_ACTIONS)


class MyAgent(Agent):
    """Phase 7: object scenes + exploration + causality + goal hypothesis hints."""

    MAX_ACTIONS = MAX_ACTIONS

    def is_done(self, frames: List[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state is GameState.WIN or self.action_counter >= self.MAX_ACTIONS

    def _available_simple(self, latest_frame: FrameData) -> List[str]:
        avail = getattr(latest_frame, "available_actions", None) or []
        names = [a.name for a in avail if hasattr(a, "name") and a.name in SIMPLE_ACTIONS]
        return names or SIMPLE_ACTIONS

    def _to_game_action(
        self,
        action_name: str,
        grid: Any,
        scene_hint: Optional[Dict[str, Any]] = None,
        causality_meta: Optional[Dict[str, Any]] = None,
        goal_meta: Optional[Dict[str, Any]] = None,
    ) -> GameAction:
        ga = getattr(GameAction, action_name)
        if ga.is_complex():
            h, w = len(grid), len(grid[0]) if grid else 0
            ga.set_data({"x": w // 2, "y": h // 2})
        sh = state_hash(grid)
        explore_meta = GLOBAL_EXPLORER.exploration.exploration_metadata(sh)
        n_obj = (scene_hint or {}).get("num_objects", "?")
        sem = (causality_meta or {}).get("semantic_label", "unknown")
        conf = (causality_meta or {}).get("confidence", 0.0)
        unc = (causality_meta or {}).get("uncertainty", 1.0)
        goal = (goal_meta or {}).get("template_id", "unknown")
        ga.reasoning = (
            f"ASRA Phase7: {action_name} | objects={n_obj} "
            f"| visits={explore_meta.get('visit_count_before', 0)} "
            f"| sem={sem} conf={conf:.2f} u={unc:.2f} "
            f"| goal={goal}"
        )
        return ga

    def choose_action(self, frames: List[FrameData], latest_frame: FrameData) -> GameAction:
        if latest_frame.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            return GameAction.RESET
        grid = latest_frame.frame
        scene = compact_scene(canonical_grid(grid))
        name, causality_meta, goal_meta = GLOBAL_EXPLORER.choose_action(
            state_hash(grid), GLOBAL_SEMANTICS, self._available_simple(latest_frame), scene_hint=scene
        )
        return self._to_game_action(name, grid, scene, causality_meta, goal_meta)

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
        transform_hist = transform_histogram_from_scenes(scene_before, scene_after)
        diff = {
            "num_changed_cells": diff_count,
            "object_scene_before": scene_before,
            "object_scene_after": scene_after,
            "transform_histogram": transform_hist,
            **object_delta(scene_before, scene_after),
        }
        reward = float(getattr(curr, "levels_completed", 0) or 0)
        level_completed = int(getattr(curr, "levels_completed", 0) or 0)
        sh = state_hash(prev_grid)
        nsh = state_hash(curr_grid)
        action = getattr(self, "_last_action_name", "UNKNOWN")
        sem = GLOBAL_SEMANTICS.infer(sh, action)
        GLOBAL_SEMANTICS.observe(sh, action, diff, reward, next_hash=nsh)
        GLOBAL_EXPLORER.update(
            sh, nsh, action, diff, reward, semantics=sem, level_completed=level_completed
        )
