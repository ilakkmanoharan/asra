from asra.agent.baseline_agent import BaselineAgent
from asra.env.arc_agi3_runner import ArcAGI3Runner


def test_runner_runs_episode(tmp_path):
    result = ArcAGI3Runner(data_dir=str(tmp_path)).run_episode(BaselineAgent(), max_steps=10)
    assert result.transitions
    assert result.final_status in {"NOT_FINISHED", "WIN", "GAME_OVER"}
