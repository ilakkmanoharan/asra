from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from asra.agent.dead_end_detector import detect_dead_end
from asra.analysis.grid_diff import diff_grid
from asra.env.arc_agi3_runner import ArcAGI3Runner, EpisodeResult
from asra.exploration.exploration_graph import ExplorationGraph
from asra.exploration.novelty import NoveltyScorer
from asra.exploration.policy_v2 import ExplorationPolicyV2
from asra.exploration.replay import TransitionReplayBuffer
from asra.exploration.subgoals import SubgoalState
from asra.exploration.usefulness import UsefulnessScorer
from asra.exploration.visitation_memory import VisitationMemory
from asra.memory.episode_logger import EpisodeLogger
from asra.memory.transition_schema import make_transition
from asra.perception.snapshot import compact_scene_dict, object_scenes_enabled, scene_from_grid
from asra.utils.hashing import hash_state


@dataclass
class ArcExplorationEpisodeResult(EpisodeResult):
    unique_nodes: int = 0
    loop_count: int = 0
    policy: str = "exploration_v2"


class ArcExplorationRunner:
    """ARC-AGI-3 episodes with Phase 3 exploration graph and dual-key novelty."""

    def __init__(
        self,
        runner: ArcAGI3Runner | None = None,
        data_dir: str = "data/arc_exploration",
        policy: ExplorationPolicyV2 | None = None,
    ) -> None:
        self.runner = runner or ArcAGI3Runner(data_dir=data_dir)
        self.data_dir = data_dir
        self.policy = policy or ExplorationPolicyV2()
        self.memory = VisitationMemory()
        self.graph = ExplorationGraph()
        self.novelty = NoveltyScorer()
        self.usefulness = UsefulnessScorer()
        self.replay = TransitionReplayBuffer()

    def run_episode(self, max_steps: int = 200, include_object_scenes: bool | None = None) -> ArcExplorationEpisodeResult:
        attach_scenes = object_scenes_enabled() if include_object_scenes is None else include_object_scenes
        logger = EpisodeLogger(self.data_dir)
        frame = self.runner.reset()
        transitions: list[dict[str, Any]] = []
        total_reward = 0.0
        recent_states = [hash_state(frame.grid)]
        loop_count = 0
        prev_level = frame.level_id
        level_subgoal = SubgoalState(
            subgoal_id="level_progress",
            index=0,
            description=f"Complete {prev_level}",
            status="active",
            entered_at_step=0,
        )

        for step in range(1, max_steps + 1):
            state_hash = hash_state(frame.grid)
            object_scene = compact_scene_dict(scene_from_grid(frame.grid)) if attach_scenes else None
            dead = detect_dead_end(state_hash, recent_states=recent_states, status=frame.status)
            decision = self.policy.select_action(
                state_hash,
                self.runner.get_available_actions(),
                self.graph,
                self.memory,
                subgoal=level_subgoal,
                object_scene=object_scene,
                precondition={"level_id": frame.level_id, "game_id": frame.game_id},
            )
            action = decision["selected_action"]
            prev = frame
            result = self.runner.step(action)
            grid_diff = diff_grid(prev.grid, result.frame.grid)
            transition = make_transition(
                logger.episode_id,
                prev,
                action,
                result.frame,
                result.reward,
                grid_diff,
                agent_version="asra-v0.5-phase3",
                policy=self.policy.name,
                notes=decision.get("reason", ""),
                include_object_scenes=attach_scenes,
            )
            next_hash = hash_state(result.frame.grid)
            if next_hash in recent_states:
                loop_count += 1
            dead_end = bool(dead.get("dead_end_score", 0.0) >= 0.8 or grid_diff.get("num_changed_cells", 0) == 0)
            frontier_gain = self.graph.frontier_gain(state_hash, next_hash)
            next_scene = compact_scene_dict(scene_from_grid(result.frame.grid)) if attach_scenes else None
            novelty_val = self.novelty.edge_novelty(
                next_hash,
                self.memory,
                reward=result.reward,
                dead_end=dead_end,
                object_scene=next_scene,
            )
            if result.frame.level_id != prev_level:
                level_subgoal.status = "completed"
                level_subgoal.completed_at_step = step
                prev_level = result.frame.level_id
                level_subgoal = SubgoalState(
                    subgoal_id="level_progress",
                    index=level_subgoal.index + 1,
                    description=f"Complete {prev_level}",
                    status="active",
                    entered_at_step=step,
                )
            usefulness_val = self.usefulness.score(
                reward_delta=result.reward,
                frontier_gain=frontier_gain,
                subgoal=level_subgoal,
                dead_end=dead_end,
                object_delta=(
                    (next_scene or {}).get("num_objects", 0) - (object_scene or {}).get("num_objects", 0)
                    if attach_scenes and object_scene and next_scene
                    else None
                ),
            )
            transition.metadata["exploration"] = {
                "novelty": novelty_val,
                "usefulness": usefulness_val,
                "visit_count_before": self.memory.visit_count(state_hash),
                "frontier_node": self.graph.frontier_score(state_hash) > 0.5,
                "dead_end": dead_end,
                "subgoal_id": level_subgoal.subgoal_id,
                "subgoal_index": level_subgoal.index,
                "loop_detected": next_hash in recent_states,
            }
            transition.metadata["dead_end_score"] = dead.get("dead_end_score", 0.0)
            row = transition.to_dict()
            logger.log_transition(transition)
            transitions.append(row)
            self.policy.observe(row)
            self.graph.add_transition(
                row, step=step, novelty_gain=novelty_val, usefulness=usefulness_val, dead_end=dead_end
            )
            self.memory.observe(next_hash, step=step, object_scene=next_scene)
            self.replay.push(row, priority=novelty_val + usefulness_val + abs(result.reward))
            total_reward += result.reward
            frame = result.frame
            recent_states.append(next_hash)
            recent_states = recent_states[-20:]
            if result.terminal_state:
                break

        summary = {
            "final_status": frame.status,
            "total_reward": total_reward,
            "num_steps": len(transitions),
            "unique_nodes": self.graph.unique_nodes(),
            "loop_count": loop_count,
        }
        logger.finalize(summary)
        graph_path = Path(self.data_dir) / "graphs" / f"{logger.episode_id}.json"
        graph_path.parent.mkdir(parents=True, exist_ok=True)
        self.graph.save(graph_path)
        return ArcExplorationEpisodeResult(
            episode_id=logger.episode_id,
            transitions=transitions,
            final_status=frame.status,
            total_reward=total_reward,
            episode_path=str(logger.episode_path),
            transition_path=str(logger.transition_path),
            unique_nodes=self.graph.unique_nodes(),
            loop_count=loop_count,
            policy=self.policy.name,
        )


def build_arc_exploration_graphs(transition_dir: str | Path, output_dir: str | Path) -> list[Path]:
    from asra.exploration.exploration_graph import ExplorationGraph
    from asra.utils.serialization import read_jsonl

    transition_dir = Path(transition_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for path in sorted(transition_dir.glob("*.jsonl")):
        graph = ExplorationGraph()
        step = 0
        for transition in read_jsonl(path):
            meta = transition.get("metadata", {}).get("exploration", {})
            graph.add_transition(
                transition,
                step=step,
                novelty_gain=float(meta.get("novelty", 0.0)),
                usefulness=float(meta.get("usefulness", 0.0)),
                dead_end=bool(meta.get("dead_end", False)),
            )
            step += 1
        out = output_dir / f"{path.stem}_exploration.json"
        graph.save(out)
        paths.append(out)
    return paths
