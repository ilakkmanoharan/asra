from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from asra.memory.transition_schema import Transition
from asra.utils.serialization import write_json


class EpisodeLogger:
    def __init__(self, data_dir: str | Path = "data", episode_id: str | None = None) -> None:
        self.data_dir = Path(data_dir)
        self.episode_id = episode_id or str(uuid4())
        self.transitions: list[dict[str, Any]] = []
        self.episodes_dir = self.data_dir / "episodes"
        self.transitions_dir = self.data_dir / "transitions"
        self.episodes_dir.mkdir(parents=True, exist_ok=True)
        self.transitions_dir.mkdir(parents=True, exist_ok=True)

    @property
    def transition_path(self) -> Path:
        return self.transitions_dir / f"{self.episode_id}.jsonl"

    @property
    def episode_path(self) -> Path:
        return self.episodes_dir / f"{self.episode_id}.json"

    def log_transition(self, transition: Transition) -> None:
        row = transition.to_dict()
        self.transitions.append(row)
        with self.transition_path.open("a", encoding="utf-8") as handle:
            import json
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    def finalize(self, summary: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = {
            "episode_id": self.episode_id,
            "num_transitions": len(self.transitions),
            "transition_log": str(self.transition_path),
            "summary": summary or {},
        }
        write_json(self.episode_path, payload)
        return payload
