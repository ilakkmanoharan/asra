from asra.exploration.exploration_graph import ExplorationGraph
from asra.exploration.visitation_memory import VisitationMemory, object_scene_fingerprint
from asra.memory.transition_schema import make_transition
from asra.env.frame_parser import parse_frame
from asra.analysis.grid_diff import diff_grid


def _sample_transition(episode_id: str = "ep1", step: int = 0, a: int = 0, b: int = 1):
    state = parse_frame(
        {"game_id": "g", "level_id": "l", "step_index": step, "grid": [[a]], "status": "NOT_FINISHED"}
    )
    nxt = parse_frame(
        {"game_id": "g", "level_id": "l", "step_index": step + 1, "grid": [[b]], "status": "NOT_FINISHED"}
    )
    return make_transition(episode_id, state, "ACTION1", nxt, 0.0, diff_grid(state.grid, nxt.grid)).to_dict()


def test_exploration_graph_tracks_nodes_and_edges():
    graph = ExplorationGraph()
    t1 = _sample_transition(step=0, a=0, b=1)
    t2 = _sample_transition(step=1, a=1, b=2)
    graph.add_transition(t1, step=0, novelty_gain=0.5)
    graph.add_transition(t2, step=1, novelty_gain=0.3)
    assert graph.unique_nodes() == 3
    assert len(graph.to_dict()["edges"]) == 2


def test_visitation_memory_counts_and_recent():
    mem = VisitationMemory(recent_window=3)
    mem.observe("h1", step=1)
    mem.observe("h2", step=2)
    mem.observe("h1", step=3)
    assert mem.visit_count("h1") == 2
    assert mem.count_in_recent("h1") == 2
    assert not mem.is_novel("h1")


def test_object_scene_fingerprint_stable():
    scene = {"num_objects": 1, "objects": [{"color": 2, "area": 3, "bbox": [0, 0, 1, 1]}]}
    assert object_scene_fingerprint(scene) == object_scene_fingerprint(scene)


def test_build_graph_from_transition_dir(tmp_path):
    import json

    path = tmp_path / "ep.jsonl"
    with path.open("w") as f:
        f.write(json.dumps(_sample_transition()) + "\n")
    graph = ExplorationGraph.from_transition_dir(tmp_path)
    assert graph.unique_nodes() >= 2
