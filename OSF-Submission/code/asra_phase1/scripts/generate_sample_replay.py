#!/usr/bin/env python3
"""Generate data/raw/sample_arc_agi3_replay.json from the mock environment."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from asra.env.action_space import SUPPORTED_ACTIONS
from asra.env.arc_agi3_runner import MockArcAGI3Environment

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "sample_arc_agi3_replay.json"


def main() -> None:
    env = MockArcAGI3Environment()
    initial = env.reset("arc-sample-replay", "level-001")
    outcomes: dict[str, object] = {"RESET": "reset"}
    for action in SUPPORTED_ACTIONS:
        if action == "RESET":
            continue
        env.reset("arc-sample-replay", "level-001")
        frame = env.step(action)
        outcomes[action] = {
            "grid": frame["grid"],
            "status": frame["status"],
            "reward": frame.get("reward", 0.0),
            "step_index": frame["step_index"],
        }
    payload = {
        "game_id": "arc-sample-replay",
        "level_id": "level-001",
        "initial": initial,
        "action_outcomes": outcomes,
        "source": "mock-derived-offline-replay",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
