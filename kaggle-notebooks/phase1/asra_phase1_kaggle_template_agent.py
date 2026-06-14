"""ASRA Phase 1 agent — Kaggle template form (no bootstrap).

Spliced into the submission notebook and copied to
/kaggle/working/ARC-AGI-3-Agents/agents/templates/my_agent.py during
competition rerun. Must subclass Agent and expose class MyAgent.
"""
from __future__ import annotations

import hashlib
import json
import random
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from arcengine import FrameData, GameAction, GameState

from agents.agent import Agent

SEED = 42
MAX_ACTIONS = 80
SIMPLE_ACTIONS = ["ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION5", "ACTION7"]

random.seed(SEED)
np.random.seed(SEED)


def canonical_grid(grid: Any) -> List[List[int]]:
    arr = np.array(grid, dtype=int)
    return arr.tolist()


def state_hash(grid: Any) -> str:
    payload = json.dumps(canonical_grid(grid), separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ActionSemanticsInferencer:
    def __init__(self) -> None:
        self.effects: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)

    def observe(self, state_hash_value: str, action: str, diff: Dict[str, Any], reward: float) -> None:
        self.effects[(state_hash_value, action)].append(
            {"num_changed_cells": diff.get("num_changed_cells"), "reward": reward}
        )

    def infer(self, state_hash_value: str, action: str) -> Dict[str, Any]:
        effects = self.effects.get((state_hash_value, action), [])
        if not effects:
            return {"observations": 0, "hypothesis": "unknown", "consistency_score": None}
        counts = [e["num_changed_cells"] for e in effects if e["num_changed_cells"] is not None]
        std = float(np.std(counts)) if counts else 0.0
        mean = float(np.mean(counts)) if counts else None
        if mean == 0:
            hyp = "no-op / blocked"
        elif mean is not None and mean <= 1.5:
            hyp = "localized cell update"
        else:
            hyp = "multi-cell transform"
        return {
            "observations": len(effects),
            "hypothesis": hyp,
            "consistency_score": float(1.0 / (1.0 + std)) if counts else None,
        }


class ASRAExplorer:
    def __init__(self, action_names: List[str]) -> None:
        self.action_names = action_names
        self.state_action_counts: Counter = Counter()
        self.action_rewards: Dict[str, List[float]] = defaultdict(list)
        self.dead_ends: set = set()

    def update(self, state_hash_value: str, action: str, diff: Dict[str, Any], reward: float) -> None:
        self.state_action_counts[(state_hash_value, action)] += 1
        self.action_rewards[action].append(float(reward))
        if diff.get("num_changed_cells") == 0 and reward <= 0:
            self.dead_ends.add((state_hash_value, action))

    def choose_action(
        self,
        state_hash_value: str,
        semantics: ActionSemanticsInferencer,
        available: Optional[List[str]] = None,
    ) -> str:
        candidates = [a for a in self.action_names if available is None or a in available] or list(
            self.action_names
        )
        scores: Dict[str, float] = {}
        for action in candidates:
            if (state_hash_value, action) in self.dead_ends:
                continue
            sem = semantics.infer(state_hash_value, action)
            c = sem.get("consistency_score")
            uncertainty = 1.0 if c is None else (1.0 - min(1.0, c))
            local = self.state_action_counts[(state_hash_value, action)]
            mean_r = float(np.mean(self.action_rewards[action])) if self.action_rewards[action] else 0.0
            scores[action] = 2.0 / (1.0 + local) + 0.7 * uncertainty + 0.5 * mean_r + random.random() * 0.05
        return max(scores.items(), key=lambda kv: kv[1])[0] if scores else random.choice(candidates)


GLOBAL_SEMANTICS = ActionSemanticsInferencer()
GLOBAL_EXPLORER = ASRAExplorer(SIMPLE_ACTIONS)


class MyAgent(Agent):
    """ASRA Phase 1 transition-centric explorer (Kaggle template)."""

    MAX_ACTIONS = MAX_ACTIONS

    def is_done(self, frames: List[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state is GameState.WIN or self.action_counter >= self.MAX_ACTIONS

    def _available_simple(self, latest_frame: FrameData) -> List[str]:
        avail = getattr(latest_frame, "available_actions", None) or []
        names = [a.name for a in avail if hasattr(a, "name") and a.name in SIMPLE_ACTIONS]
        return names or SIMPLE_ACTIONS

    def _to_game_action(self, action_name: str, grid: Any) -> GameAction:
        ga = getattr(GameAction, action_name)
        if ga.is_complex():
            h, w = len(grid), len(grid[0]) if grid else 0
            ga.set_data({"x": w // 2, "y": h // 2})
        ga.reasoning = f"ASRA v0.1-phase1: {action_name}"
        return ga

    def choose_action(self, frames: List[FrameData], latest_frame: FrameData) -> GameAction:
        if latest_frame.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            return GameAction.RESET
        grid = latest_frame.frame
        name = GLOBAL_EXPLORER.choose_action(
            state_hash(grid), GLOBAL_SEMANTICS, self._available_simple(latest_frame)
        )
        return self._to_game_action(name, grid)

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
        diff_count = int(np.sum(np.array(prev.frame) != np.array(curr.frame)))
        diff = {"num_changed_cells": diff_count}
        reward = float(getattr(curr, "levels_completed", 0) or 0)
        sh = state_hash(prev.frame)
        action = getattr(self, "_last_action_name", "UNKNOWN")
        GLOBAL_SEMANTICS.observe(sh, action, diff, reward)
        GLOBAL_EXPLORER.update(sh, action, diff, reward)
