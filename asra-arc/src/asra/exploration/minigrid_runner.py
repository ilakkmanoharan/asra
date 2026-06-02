from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from asra.exploration.policy_adapter import ExplorationAgent, Phase1PolicyAdapter
from asra.exploration.policy_v2 import ExplorationPolicyV2
from asra.exploration.runner_core import GymEpisodeResult, GymExplorationRunner, run_gym_batch
from asra.exploration.subgoals import SubgoalDetector


@dataclass
class MiniGridEpisodeResult(GymEpisodeResult):
    pass


class MiniGridRunner(GymExplorationRunner):
    """Run MiniGrid episodes with Phase 3 exploration engine."""

    def run_episode(
        self,
        env_id: str = "MiniGrid-Empty-8x8-v0",
        max_steps: int = 200,
        seed: int = 42,
        include_object_scenes: bool = False,
    ) -> MiniGridEpisodeResult:
        detector = SubgoalDetector.for_doorkey() if "DoorKey" in env_id else None
        result = super().run_episode(
            env_id=env_id,
            max_steps=max_steps,
            seed=seed,
            include_object_scenes=include_object_scenes,
            subgoal_detector=detector,
        )
        return MiniGridEpisodeResult(**result.__dict__)


def run_minigrid_batch(
    env_id: str,
    episodes: int = 10,
    max_steps: int = 200,
    data_dir: str = "data/minigrid",
    seed: int = 42,
    policy: ExplorationAgent | None = None,
    export_replay_path: str | Path | None = None,
) -> list[MiniGridEpisodeResult]:
    factory = SubgoalDetector.for_doorkey if "DoorKey" in env_id else None
    results = run_gym_batch(
        env_id=env_id,
        episodes=episodes,
        max_steps=max_steps,
        data_dir=data_dir,
        seed=seed,
        policy=policy or ExplorationPolicyV2(),
        subgoal_factory=factory,
        export_replay_path=export_replay_path or Path(data_dir) / "replay" / "top_transitions.jsonl",
    )
    return [MiniGridEpisodeResult(**r.__dict__) for r in results]


def run_minigrid_baseline_batch(
    env_id: str,
    episodes: int = 10,
    max_steps: int = 200,
    data_dir: str = "data/minigrid/baseline",
    seed: int = 42,
) -> list[MiniGridEpisodeResult]:
    return run_minigrid_batch(
        env_id=env_id,
        episodes=episodes,
        max_steps=max_steps,
        data_dir=data_dir,
        seed=seed,
        policy=Phase1PolicyAdapter(),
        export_replay_path=None,
    )
