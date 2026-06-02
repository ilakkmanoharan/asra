from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from asra.analysis.grid_diff import diff_grid
from asra.env.frame_parser import Frame
from asra.exploration.env_utils import (
    asra_action_names,
    encode_minigrid_grid,
    minigrid_action_label,
    minigrid_precondition,
    status_from_gym,
)
from asra.exploration.novelty import NoveltyScorer
from asra.exploration.policy_adapter import ExplorationAgent
from asra.exploration.policy_v2 import ExplorationPolicyV2
from asra.exploration.session import ExplorationSessionState
from asra.exploration.strategies import StrategyLibrary, default_doorkey_strategy
from asra.exploration.subgoals import SubgoalDetector
from asra.exploration.usefulness import UsefulnessScorer
from asra.memory.episode_logger import EpisodeLogger
from asra.memory.transition_schema import make_transition
from asra.utils.hashing import hash_state


@dataclass
class GymEpisodeResult:
    episode_id: str
    env_id: str
    steps: int
    total_reward: float
    success: bool
    unique_nodes: int
    transition_path: str
    strategy_reused: bool = False
    subgoal_completions: int = 0


class GymExplorationRunner:
    """Shared MiniGrid/BabyAI episode loop with Phase 3 exploration metadata."""

    def __init__(
        self,
        data_dir: str = "data/minigrid",
        policy: ExplorationAgent | None = None,
        session: ExplorationSessionState | None = None,
        seed_doorkey_strategy: bool = True,
    ) -> None:
        self.data_dir = data_dir
        self.session = session or ExplorationSessionState.fresh()
        self.novelty = NoveltyScorer()
        self.usefulness = UsefulnessScorer()
        if seed_doorkey_strategy and not self.session.strategies.to_list():
            self.session.strategies.add(default_doorkey_strategy())
        if policy is None:
            self.policy: ExplorationAgent = ExplorationPolicyV2(strategy_library=self.session.strategies)
        elif isinstance(policy, ExplorationPolicyV2):
            policy.strategies = self.session.strategies
            self.policy = policy
        else:
            self.policy = policy

    @property
    def memory(self):
        return self.session.memory

    @property
    def graph(self):
        return self.session.graph

    @property
    def strategies(self) -> StrategyLibrary:
        return self.session.strategies

    @property
    def replay(self):
        return self.session.replay

    def run_episode(
        self,
        env_id: str = "MiniGrid-Empty-8x8-v0",
        max_steps: int = 200,
        seed: int = 42,
        include_object_scenes: bool = False,
        subgoal_detector: SubgoalDetector | None = None,
        mission: str | None = None,
    ) -> GymEpisodeResult:
        import gymnasium as gym
        import minigrid  # noqa: F401

        env = gym.make(env_id)
        env.reset(seed=seed)
        if mission and hasattr(env.unwrapped, "mission"):
            env.unwrapped.mission = mission

        episode_id = str(uuid4())
        logger = EpisodeLogger(self.data_dir, episode_id=episode_id)
        total_reward = 0.0
        step = 0
        success = False
        strategy_reused = False
        subgoal_completions = 0
        episode_transitions: list[dict[str, Any]] = []

        grid = encode_minigrid_grid(env)
        prev = Frame(
            game_id=env_id,
            level_id="L0",
            step_index=0,
            grid=grid,
            height=len(grid),
            width=len(grid[0]) if grid else 0,
            status="NOT_FINISHED",
            metadata={"source": "minigrid", "mission": mission or getattr(env.unwrapped, "mission", "")},
        )
        state_hash = hash_state(prev.grid)
        self.memory.observe(state_hash, step=0)

        while step < max_steps:
            available = list(range(env.action_space.n))
            action_names = asra_action_names(len(available))
            precondition = minigrid_precondition(env, env_id)
            active_subgoal = subgoal_detector.active_subgoal() if subgoal_detector else None
            object_scene = None
            if include_object_scenes:
                from asra.perception.snapshot import compact_scene_dict, scene_from_grid

                object_scene = compact_scene_dict(scene_from_grid(prev.grid))

            decision = self.policy.select_action(
                state_hash,
                action_names,
                self.graph,
                self.memory,
                subgoal=active_subgoal,
                object_scene=object_scene,
                precondition=precondition,
            )
            if decision.get("reason") == "strategy_bias":
                strategy_reused = True

            action_name = decision["selected_action"]
            action_idx = action_names.index(action_name)
            minigrid_action = minigrid_action_label(action_idx)

            _obs, reward, terminated, truncated, _info = env.step(action_idx)
            total_reward += float(reward)
            step += 1
            success = success or bool(terminated and reward > 0)

            next_grid = encode_minigrid_grid(env)
            status = status_from_gym(terminated, truncated)
            nxt = Frame(
                game_id=env_id,
                level_id="L0",
                step_index=step,
                grid=next_grid,
                height=len(next_grid),
                width=len(next_grid[0]) if next_grid else 0,
                status=status,
                metadata={"source": "minigrid", "mission": mission or getattr(env.unwrapped, "mission", "")},
            )
            next_hash = hash_state(nxt.grid)
            dead_end = reward <= 0 and prev.grid == nxt.grid
            frontier_gain = self.graph.frontier_gain(state_hash, next_hash)

            next_object_scene = None
            if include_object_scenes:
                from asra.perception.snapshot import compact_scene_dict, scene_from_grid

                next_object_scene = compact_scene_dict(scene_from_grid(nxt.grid))

            novelty_val = self.novelty.edge_novelty(
                next_hash,
                self.memory,
                reward=reward,
                dead_end=dead_end,
                object_scene=next_object_scene,
            )
            subgoal_complete = False
            completed_subgoal_id: str | None = None
            if subgoal_detector:
                before = sum(1 for sg in subgoal_detector.subgoals if sg.status == "completed")
                subgoal_detector.update(env, step, terminated=terminated, reward=reward)
                after = sum(1 for sg in subgoal_detector.subgoals if sg.status == "completed")
                if after > before:
                    subgoal_completions += after - before
                    subgoal_complete = True
                    for sg in subgoal_detector.subgoals:
                        if sg.completed_at_step == step:
                            completed_subgoal_id = sg.subgoal_id
                            break
                active_subgoal = subgoal_detector.active_subgoal()

            usefulness_val = self.usefulness.score(
                reward_delta=reward,
                frontier_gain=frontier_gain,
                subgoal=active_subgoal,
                dead_end=dead_end,
                object_delta=(
                    (next_object_scene or {}).get("num_objects", 0) - (object_scene or {}).get("num_objects", 0)
                    if include_object_scenes and object_scene and next_object_scene
                    else None
                ),
            )

            diff = diff_grid(prev.grid, nxt.grid)
            transition = make_transition(
                episode_id,
                prev,
                action_name,
                nxt,
                reward,
                diff,
                agent_version="asra-v0.5-phase3",
                policy=self.policy.name,
                notes=decision.get("reason", ""),
                include_object_scenes=include_object_scenes,
            )
            strategy_hint = self.strategies.strategy_hint(precondition)
            transition.metadata["exploration"] = {
                "novelty": novelty_val,
                "usefulness": usefulness_val,
                "visit_count_before": self.memory.visit_count(state_hash),
                "frontier_node": self.graph.frontier_score(state_hash) > 0.5,
                "dead_end": dead_end,
                "subgoal_id": active_subgoal.subgoal_id if active_subgoal else None,
                "subgoal_index": active_subgoal.index if active_subgoal else None,
                "subgoal_complete": subgoal_complete,
                "subgoal_complete_id": completed_subgoal_id,
                "strategy_hint": strategy_hint,
            }
            transition.metadata["minigrid_action"] = minigrid_action
            if mission:
                transition.metadata["mission"] = mission

            row = transition.to_dict()
            logger.log_transition(transition)
            episode_transitions.append(row)
            self.policy.observe(row)
            self.graph.add_transition(
                row, step=step, novelty_gain=novelty_val, usefulness=usefulness_val, dead_end=dead_end
            )
            self.memory.observe(next_hash, step=step, object_scene=next_object_scene)
            replay_priority = novelty_val + usefulness_val + abs(reward)
            if subgoal_completions:
                replay_priority += 2.0
            if success:
                replay_priority += 5.0
            self.replay.push(row, priority=replay_priority)

            prev = nxt
            state_hash = next_hash
            if terminated or truncated:
                break

        env.close()
        if success:
            self.strategies.extract_from_episode(
                episode_transitions,
                minigrid_precondition_from_transitions(episode_transitions, env_id),
                env_id,
            )

        logger.finalize(
            {
                "env_id": env_id,
                "steps": step,
                "total_reward": total_reward,
                "success": success,
                "unique_nodes": self.graph.unique_nodes(),
                "strategy_reused": strategy_reused,
                "subgoal_completions": subgoal_completions,
            }
        )
        return GymEpisodeResult(
            episode_id=episode_id,
            env_id=env_id,
            steps=step,
            total_reward=total_reward,
            success=success,
            unique_nodes=self.graph.unique_nodes(),
            transition_path=str(logger.transition_path),
            strategy_reused=strategy_reused,
            subgoal_completions=subgoal_completions,
        )


def minigrid_precondition_from_transitions(transitions: list[dict[str, Any]], env_id: str) -> dict[str, Any]:
    if not transitions:
        return {"env_type": "doorkey" if "DoorKey" in env_id else "minigrid"}
    first = transitions[0].get("state", {}).get("grid") or []
    carrying = False
    if first and len(first) > 0:
        agent_row = first[-1]
        carrying = len(agent_row) > 3 and agent_row[3] == 1
    return {
        "env_type": "doorkey" if "DoorKey" in env_id else "minigrid",
        "has_key": carrying,
        "door_open": False,
    }


def run_gym_batch(
    env_id: str,
    episodes: int = 10,
    max_steps: int = 200,
    data_dir: str = "data/minigrid",
    seed: int = 42,
    policy: ExplorationAgent | None = None,
    shared_session: bool = True,
    subgoal_factory: Any | None = None,
    include_object_scenes: bool = False,
    export_replay_path: str | Path | None = None,
) -> list[GymEpisodeResult]:
    from pathlib import Path

    session = ExplorationSessionState.fresh()
    results: list[GymEpisodeResult] = []
    for i in range(episodes):
        runner = GymExplorationRunner(
            data_dir=data_dir,
            policy=policy,
            session=session if shared_session else ExplorationSessionState.fresh(),
        )
        detector = subgoal_factory() if subgoal_factory else None
        results.append(
            runner.run_episode(
                env_id=env_id,
                max_steps=max_steps,
                seed=seed + i,
                include_object_scenes=include_object_scenes,
                subgoal_detector=detector,
            )
        )
    if export_replay_path:
        session.replay.export(Path(export_replay_path))
    return results
