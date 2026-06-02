from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from asra.exploration.policy_v2 import ExplorationPolicyV2
from asra.exploration.runner_core import GymEpisodeResult, GymExplorationRunner, run_gym_batch
from asra.exploration.subgoals import SubgoalDetector


@dataclass
class BabyAIEpisodeResult(GymEpisodeResult):
    mission: str = ""


class BabyAIRunner(GymExplorationRunner):
    """Run BabyAI episodes with mission parsing and subgoal tagging."""

    def __init__(self, data_dir: str = "data/babyai", policy: ExplorationPolicyV2 | None = None) -> None:
        super().__init__(data_dir=data_dir, policy=policy or ExplorationPolicyV2(), seed_doorkey_strategy=False)

    def run_episode(
        self,
        env_id: str = "BabyAI-GoToRedBallGrey-v0",
        max_steps: int = 200,
        seed: int = 42,
        include_object_scenes: bool = False,
    ) -> BabyAIEpisodeResult:
        import gymnasium as gym
        import minigrid  # noqa: F401

        env = gym.make(env_id)
        env.reset(seed=seed)
        mission = str(getattr(env.unwrapped, "mission", ""))
        env.close()

        detector = SubgoalDetector.from_mission(mission)
        result = super().run_episode(
            env_id=env_id,
            max_steps=max_steps,
            seed=seed,
            include_object_scenes=include_object_scenes,
            subgoal_detector=detector,
            mission=mission,
        )
        return BabyAIEpisodeResult(**result.__dict__, mission=mission)


def run_babyai_batch(
    env_id: str = "BabyAI-GoToRedBallGrey-v0",
    episodes: int = 10,
    max_steps: int = 200,
    data_dir: str = "data/babyai",
    seed: int = 42,
    export_replay_path: str | Path | None = None,
) -> list[BabyAIEpisodeResult]:
    runner = BabyAIRunner(data_dir=data_dir)
    results: list[BabyAIEpisodeResult] = []
    for i in range(episodes):
        results.append(runner.run_episode(env_id=env_id, max_steps=max_steps, seed=seed + i))
    if export_replay_path:
        runner.replay.export(Path(export_replay_path))
    elif episodes:
        runner.replay.export(Path(data_dir) / "replay" / "top_transitions.jsonl")
    return results
