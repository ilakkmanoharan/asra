from pathlib import Path

from asra.analysis.grid_diff import diff_grid
from asra.env.frame_parser import parse_frame
from asra.export.dataset_exporter import export_dataset
from asra.memory.episode_logger import EpisodeLogger
from asra.memory.transition_schema import make_transition


def test_make_transition_object_scenes(tmp_path):
    state = parse_frame({"game_id": "g", "level_id": "l", "step_index": 0, "grid": [[0, 1], [0, 0]], "status": "NOT_FINISHED"})
    next_state = parse_frame({"game_id": "g", "level_id": "l", "step_index": 1, "grid": [[0, 0], [1, 0]], "status": "NOT_FINISHED"})
    transition = make_transition(
        "ep1",
        state,
        "ACTION1",
        next_state,
        0.0,
        diff_grid(state.grid, next_state.grid),
        include_object_scenes=True,
    )
    assert transition.metadata["object_scenes_attached"] is True
    assert "object_scene" in transition.state
    assert "object_scene" in transition.next_state
    assert transition.state["object_scene"]["num_objects"] >= 1


def test_dataset_exporter_object_scene_columns(tmp_path):
    logger = EpisodeLogger(tmp_path, episode_id="ep1")
    state = parse_frame({"game_id": "g", "level_id": "l", "step_index": 0, "grid": [[2, 2], [0, 0]], "status": "NOT_FINISHED"})
    next_state = parse_frame({"game_id": "g", "level_id": "l", "step_index": 1, "grid": [[2, 2], [2, 0]], "status": "NOT_FINISHED"})
    transition = make_transition(
        "ep1",
        state,
        "ACTION1",
        next_state,
        0.0,
        diff_grid(state.grid, next_state.grid),
        include_object_scenes=True,
    )
    logger.log_transition(transition)
    paths = export_dataset(tmp_path / "transitions", tmp_path / "exports")
    import pandas as pd

    df = pd.read_parquet(paths["parquet"])
    assert "state_num_objects" in df.columns
    assert "next_state_num_objects" in df.columns
    assert bool(df.loc[0, "object_scenes_attached"])
    assert df.loc[0, "state_num_objects"] >= 1


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
