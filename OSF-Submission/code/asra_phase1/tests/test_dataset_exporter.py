from pathlib import Path

from asra.analysis.grid_diff import diff_grid
from asra.env.frame_parser import parse_frame
from asra.export.dataset_exporter import export_dataset
from asra.memory.episode_logger import EpisodeLogger
from asra.memory.transition_schema import make_transition


def test_dataset_exporter_outputs_files(tmp_path):
    logger = EpisodeLogger(tmp_path, episode_id="ep1")
    state = parse_frame({"game_id": "g", "level_id": "l", "step_index": 0, "grid": [[0]], "status": "NOT_FINISHED"})
    next_state = parse_frame({"game_id": "g", "level_id": "l", "step_index": 1, "grid": [[1]], "status": "WIN"})
    transition = make_transition("ep1", state, "ACTION1", next_state, 1.0, diff_grid(state.grid, next_state.grid))
    logger.log_transition(transition)
    paths = export_dataset(tmp_path / "transitions", tmp_path / "exports")
    assert Path(paths["jsonl"]).exists()
    assert Path(paths["parquet"]).exists()
    assert Path(paths["summary_csv"]).exists()
    assert Path(paths["state_graph"]).exists()
