"""Replay ARC-AGI-3 frames from a JSON file (official-style offline backend)."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from asra.env.action_space import SUPPORTED_ACTIONS


class ReplayArcAGI3Environment:
    """Step through pre-recorded action → frame outcomes for reproducible ARC-AGI-3 runs."""

    def __init__(self, replay_path: str | Path) -> None:
        payload = json.loads(Path(replay_path).read_text(encoding="utf-8"))
        self.game_id = payload["game_id"]
        self.level_id = payload["level_id"]
        self._initial = deepcopy(payload["initial"])
        self._outcomes: dict[str, Any] = payload.get("action_outcomes", {})
        self._frame = deepcopy(self._initial)
        self.step_index = 0

    def reset(self, game_id: str = "", level_id: str = "") -> dict[str, Any]:
        self.game_id = game_id or self.game_id
        self.level_id = level_id or self.level_id
        self._frame = deepcopy(self._initial)
        self._frame["game_id"] = self.game_id
        self._frame["level_id"] = self.level_id
        self.step_index = 0
        self._frame["step_index"] = 0
        return deepcopy(self._frame)

    def step(self, action: str) -> dict[str, Any]:
        self.step_index += 1
        if action == "RESET":
            return self.reset(self.game_id, self.level_id)
        outcome = self._outcomes.get(action)
        if outcome is None:
            return self._noop(action)
        if outcome == "reset":
            return self.reset(self.game_id, self.level_id)
        frame = deepcopy(outcome)
        frame["game_id"] = self.game_id
        frame["level_id"] = self.level_id
        frame["step_index"] = self.step_index
        self._frame = frame
        return deepcopy(frame)

    def get_available_actions(self) -> list[str]:
        return SUPPORTED_ACTIONS.copy()

    def _noop(self, action: str) -> dict[str, Any]:
        frame = deepcopy(self._frame)
        frame["step_index"] = self.step_index
        frame.setdefault("metadata", {})["unknown_action"] = action
        return frame
