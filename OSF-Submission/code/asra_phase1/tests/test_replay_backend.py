import json
from pathlib import Path

from asra.env.replay_backend import ReplayArcAGI3Environment


def test_replay_backend_reset_and_step(tmp_path):
    payload = {
        "game_id": "g1",
        "level_id": "l1",
        "initial": {"grid": [[0]], "status": "NOT_FINISHED", "reward": 0.0, "step_index": 0},
        "action_outcomes": {
            "ACTION1": {"grid": [[1]], "status": "NOT_FINISHED", "reward": 0.0},
            "RESET": "reset",
        },
    }
    path = tmp_path / "replay.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    env = ReplayArcAGI3Environment(path)
    frame = env.reset("g1", "l1")
    assert frame["grid"] == [[0]]
    next_frame = env.step("ACTION1")
    assert next_frame["grid"] == [[1]]
    reset_frame = env.step("RESET")
    assert reset_frame["grid"] == [[0]]
