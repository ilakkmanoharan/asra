import json

from asra.analysis.grid_diff import diff_grid
from asra.env.frame_parser import parse_frame
from asra.memory.episode_logger import EpisodeLogger
from asra.memory.transition_schema import make_transition


def test_episode_logger_writes_jsonl(tmp_path):
    logger = EpisodeLogger(tmp_path, episode_id="ep1")
    state = parse_frame({"game_id": "g", "level_id": "l", "step_index": 0, "grid": [[0]], "status": "NOT_FINISHED"})
    next_state = parse_frame({"game_id": "g", "level_id": "l", "step_index": 1, "grid": [[1]], "status": "NOT_FINISHED"})
    transition = make_transition("ep1", state, "ACTION1", next_state, 0.0, diff_grid(state.grid, next_state.grid))
    logger.log_transition(transition)
    logger.finalize()
    rows = [json.loads(line) for line in logger.transition_path.read_text().splitlines()]
    assert rows[0]["episode_id"] == "ep1"
    assert rows[0]["state"]["state_hash"]
    assert logger.episode_path.exists()
