from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from asra.agent.action_report_store import maybe_save_action_report
from asra.agent.dead_end_detector import detect_dead_end
from asra.analysis.grid_diff import diff_grid
from asra.env.action_space import SUPPORTED_ACTIONS
from asra.env.frame_parser import Frame, parse_frame
from asra.memory.episode_logger import EpisodeLogger
from asra.memory.transition_schema import make_transition
from asra.utils.hashing import hash_state


@dataclass
class StepResult:
    frame: Frame
    reward: float
    terminal_state: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EpisodeResult:
    episode_id: str
    transitions: list[dict[str, Any]]
    final_status: str
    total_reward: float
    episode_path: str
    transition_path: str


class EnvironmentBackend(Protocol):
    def reset(self, game_id: str, level_id: str) -> dict[str, Any]: ...
    def step(self, action: str) -> dict[str, Any]: ...
    def get_available_actions(self) -> list[str]: ...


class MockArcAGI3Environment:
    def __init__(self, scenario: str = "default") -> None:
        self.step_index = 0
        self.grid = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
        self.game_id = "mock-game"
        self.level_id = "mock-level"
        self.scenario = scenario
        self._episode_steps = 0

    def reset(self, game_id: str = "mock-game", level_id: str = "mock-level") -> dict[str, Any]:
        self.step_index = 0
        self.game_id = game_id
        self.level_id = level_id
        self.grid = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
        if self.scenario != "terminal_demo":
            self._episode_steps = 0
        return self._frame("NOT_FINISHED", 0.0)

    def step(self, action: str) -> dict[str, Any]:
        self.step_index += 1
        self._episode_steps = getattr(self, "_episode_steps", 0) + 1
        if action == "RESET":
            frame = self.reset(self.game_id, self.level_id)
            if self.scenario == "terminal_demo":
                self._episode_steps = getattr(self, "_episode_steps", 0)
            return frame
        y = (SUPPORTED_ACTIONS.index(action) - 1) // 3 if action in SUPPORTED_ACTIONS[1:] else 0
        x = (SUPPORTED_ACTIONS.index(action) - 1) % 3 if action in SUPPORTED_ACTIONS[1:] else 0
        self.grid[y][x] = (self.grid[y][x] + 1) % 4
        if self.scenario == "terminal_demo" and self._episode_steps >= 4:
            status, reward = "WIN", 1.0
        elif self.scenario == "game_over_demo" and self._episode_steps >= 3:
            status, reward = "GAME_OVER", 0.0
        else:
            status = "WIN" if self.step_index >= 6 and sum(map(sum, self.grid)) >= 6 else "NOT_FINISHED"
            reward = 1.0 if status == "WIN" else 0.0
        return self._frame(status, reward)

    def get_available_actions(self) -> list[str]:
        return SUPPORTED_ACTIONS.copy()

    def _frame(self, status: str, reward: float) -> dict[str, Any]:
        return {"game_id": self.game_id, "level_id": self.level_id, "step_index": self.step_index, "grid": [row[:] for row in self.grid], "status": status, "reward": reward}


class ArcAGI3Runner:
    def __init__(self, backend: EnvironmentBackend | None = None, game_id: str = "mock-game", level_id: str = "mock-level", data_dir: str = "data") -> None:
        self.backend = backend or MockArcAGI3Environment()
        self.game_id = game_id
        self.level_id = level_id
        self.data_dir = data_dir
        self.current_frame: Frame | None = None

    def reset(self) -> Frame:
        self.current_frame = parse_frame(self.backend.reset(self.game_id, self.level_id))
        return self.current_frame

    def step(self, action: str) -> StepResult:
        raw = self.backend.step(action)
        frame = parse_frame(raw)
        self.current_frame = frame
        return StepResult(frame=frame, reward=float(raw.get("reward", 0.0)), terminal_state=frame.status in {"WIN", "GAME_OVER"}, metadata=raw.get("metadata", {}))

    def get_available_actions(self) -> list[str]:
        return self.backend.get_available_actions()

    def run_episode(self, agent: Any, max_steps: int = 200) -> EpisodeResult:
        logger = EpisodeLogger(self.data_dir)
        reports_dir = Path(self.data_dir) / "analysis" / "action_reports"
        frame = self.reset()
        transitions: list[dict[str, Any]] = []
        total_reward = 0.0
        recent_states = [hash_state(frame.grid)]
        for _ in range(max_steps):
            state_hash = hash_state(frame.grid)
            dead = detect_dead_end(state_hash, recent_states=recent_states, status=frame.status)
            decision = agent.select_action(state_hash, self.get_available_actions(), dead.get("dead_end_score", 0.0))
            action = decision["selected_action"] if isinstance(decision, dict) else str(decision)
            prev = frame
            result = self.step(action)
            grid_diff = diff_grid(prev.grid, result.frame.grid)
            transition = make_transition(logger.episode_id, prev, action, result.frame, result.reward, grid_diff, policy=getattr(agent, "name", "simple_exploration"), notes=(decision.get("reason", "") if isinstance(decision, dict) else ""))
            row = transition.to_dict()
            row["metadata"]["dead_end_score"] = dead.get("dead_end_score", 0.0)
            logger.log_transition(transition)
            transitions.append(row)
            if hasattr(agent, "observe"):
                agent.observe(row)
            if hasattr(agent, "action_memory"):
                state_payload = row["state"]
                report = maybe_save_action_report(
                    state_payload,
                    self.get_available_actions(),
                    agent.action_memory,
                    reports_dir,
                )
                if report:
                    row["metadata"]["action_test_report_id"] = report["state_hash"]
            total_reward += result.reward
            frame = result.frame
            recent_states.append(hash_state(frame.grid))
            recent_states = recent_states[-20:]
            if result.terminal_state:
                break
        summary = {"final_status": frame.status, "total_reward": total_reward, "num_steps": len(transitions)}
        episode_payload = logger.finalize(summary)
        return EpisodeResult(
            logger.episode_id,
            transitions,
            frame.status,
            total_reward,
            str(logger.episode_path),
            str(logger.transition_path),
        )
