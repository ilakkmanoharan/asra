from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from asra.goals import (  # noqa: E402
    GoalHypothesisGenerator,
    GoalsStore,
    HypothesisRanker,
    ObjectRoleClassifier,
    ProgressDetector,
    build_goals_from_transitions,
    eval_goals_on_transitions,
)


def test_generator_spawns_templates():
    gen = GoalHypothesisGenerator()
    scene = {"num_objects": 3, "objects": [{}, {}, {}]}
    hyps = gen.generate("g1", scene)
    assert len(hyps) >= 5
    assert any(h.template_id == "move_to_target" for h in hyps)


def test_object_roles():
    scene = {
        "num_objects": 2,
        "objects": [
            {"object_id": "obj_0", "area": 10, "color": 1, "bbox": [0, 0, 4, 4]},
            {"object_id": "obj_1", "area": 2, "color": 2, "bbox": [5, 5, 6, 6]},
        ],
    }
    roles = ObjectRoleClassifier().roles_dict(scene)
    assert "obj_0" in roles
    assert roles["obj_0"] in ("agent", "target", "unknown")


def test_progress_detector_reward():
    det = ProgressDetector()
    sigs = det.detect(
        episode_id="e1",
        step=1,
        state_hash="h1",
        action="ACTION1",
        reward=1.0,
        level_completed=1,
        semantic_label="translate",
        diff={"delta_num_objects": 0},
    )
    types = {s.signal_type for s in sigs}
    assert "reward" in types
    assert "level_up" in types


def test_ranker_updates():
    gen = GoalHypothesisGenerator()
    hyps = gen.generate("g1", {"num_objects": 2, "objects": [{}, {}]})
    ranker = HypothesisRanker()
    det = ProgressDetector()
    sigs = det.detect(
        episode_id="e1",
        step=1,
        state_hash="h1",
        action="ACTION1",
        reward=0.0,
        level_completed=0,
        semantic_label="translate",
        diff={},
    )
    for h in hyps:
        for s in sigs:
            ranker.update_from_signal(h, s)
    ranked = ranker.rank(hyps)
    assert ranked[0].status == "leading"


def test_goals_store_ingest(tmp_path):
    store = GoalsStore()
    t = {
        "game_id": "mock",
        "episode_id": "ep1",
        "step": 1,
        "state": {"state_hash": "abc"},
        "action": {"name": "ACTION1"},
        "reward": 1.0,
        "diff": {"object_scene_after": {"num_objects": 2, "objects": [{}, {}]}},
        "metadata": {"causality": {"semantic_label": "translate"}},
    }
    out = store.ingest_transition(t)
    assert "goals" in out["metadata"]
    paths = store.save(tmp_path)
    assert (tmp_path / "hypotheses" / "mock.json").is_file()


def test_build_and_eval_empty_dir(tmp_path):
    trans = tmp_path / "transitions"
    trans.mkdir()
    line = {
        "game_id": "g",
        "episode_id": "e",
        "step": 0,
        "state": {"state_hash": "s1"},
        "action": {"name": "ACTION2"},
        "reward": 0,
        "diff": {"object_scene_after": {"num_objects": 3, "objects": [{}, {}, {}]}},
        "metadata": {},
    }
    (trans / "t.jsonl").write_text(json.dumps(line) + "\n", encoding="utf-8")
    result = build_goals_from_transitions(trans, tmp_path / "goals")
    assert result["transitions_processed"] == 1
    metrics = eval_goals_on_transitions(trans)
    assert metrics["games_with_hypotheses"] >= 1.0
