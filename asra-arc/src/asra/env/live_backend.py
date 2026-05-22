"""Live ARC-AGI-3 API backend (optional; requires credentials in environment)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from asra.env.action_space import SUPPORTED_ACTIONS
class LiveArcAGI3Environment:
    """HTTP adapter for ARC-AGI-3 when endpoint and API key are configured."""

    def __init__(self) -> None:
        self.endpoint = (os.getenv("ASRA_ARC_AGI3_ENDPOINT") or "").rstrip("/")
        self.api_key = os.getenv("ASRA_ARC_AGI3_API_KEY") or ""
        self.game_id = "live-game"
        self.level_id = "live-level"
        self._session_id: str | None = None

    def reset(self, game_id: str, level_id: str) -> dict[str, Any]:
        if not self.endpoint:
            raise RuntimeError(
                "Live ARC-AGI-3 requires ASRA_ARC_AGI3_ENDPOINT and ASRA_ARC_AGI3_API_KEY. "
                "Use --mock or --replay-file for Phase 1 offline runs."
            )
        self.game_id = game_id
        self.level_id = level_id
        payload = self._post("/reset", {"game_id": game_id, "level_id": level_id})
        return self._normalize_frame(payload)

    def step(self, action: str) -> dict[str, Any]:
        payload = self._post("/step", {"session_id": self._session_id, "action": action})
        return self._normalize_frame(payload)

    def get_available_actions(self) -> list[str]:
        return SUPPORTED_ACTIONS.copy()

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            f"{self.endpoint}{path}",
            data=data,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"ARC-AGI-3 API request failed: {exc}") from exc
        if "session_id" in payload:
            self._session_id = payload["session_id"]
        return payload.get("frame", payload)

    def _normalize_frame(self, raw: dict[str, Any]) -> dict[str, Any]:
        frame = dict(raw)
        frame.setdefault("game_id", self.game_id)
        frame.setdefault("level_id", self.level_id)
        frame.setdefault("status", "NOT_FINISHED")
        frame.setdefault("reward", 0.0)
        return frame
