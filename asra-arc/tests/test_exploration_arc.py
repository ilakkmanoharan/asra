from asra.exploration.arc_exploration import ArcExplorationRunner
from asra.env.arc_agi3_runner import ArcAGI3Runner


def test_arc_exploration_episode_mock() -> None:
    runner = ArcExplorationRunner(ArcAGI3Runner(data_dir="data/test_arc_exploration"))
    result = runner.run_episode(max_steps=15, include_object_scenes=False)
    assert result.episode_id
    assert len(result.transitions) > 0
    assert result.unique_nodes >= 1
    assert result.policy == "exploration_v2"
    for row in result.transitions:
        assert "exploration" in row["metadata"]
