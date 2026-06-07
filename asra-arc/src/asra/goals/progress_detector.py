from __future__ import annotations

from typing import Any

from asra.goals.schemas import ProgressSignal, ProgressSignalType


class ProgressDetector:
    def __init__(self) -> None:
        self._counter = 0
        self._last_level: dict[str, int] = {}

    def _next_id(self) -> str:
        self._counter += 1
        return f"prog_{self._counter}"

    def detect(
        self,
        *,
        episode_id: str,
        step: int,
        state_hash: str,
        action: str,
        reward: float,
        level_completed: int,
        semantic_label: str,
        diff: dict[str, Any],
        terminal_win: bool = False,
    ) -> list[ProgressSignal]:
        signals: list[ProgressSignal] = []
        if reward > 0:
            signals.append(
                ProgressSignal(
                    signal_id=self._next_id(),
                    episode_id=episode_id,
                    step=step,
                    signal_type="reward",
                    magnitude=float(reward),
                    state_hash=state_hash,
                    action=action,
                    semantic_label=semantic_label,
                )
            )
        prev_level = self._last_level.get(episode_id, 0)
        if level_completed > prev_level:
            self._last_level[episode_id] = level_completed
            signals.append(
                ProgressSignal(
                    signal_id=self._next_id(),
                    episode_id=episode_id,
                    step=step,
                    signal_type="level_up",
                    magnitude=float(level_completed - prev_level),
                    state_hash=state_hash,
                    action=action,
                    semantic_label=semantic_label,
                )
            )
        if terminal_win:
            signals.append(
                ProgressSignal(
                    signal_id=self._next_id(),
                    episode_id=episode_id,
                    step=step,
                    signal_type="win",
                    magnitude=1.0,
                    state_hash=state_hash,
                    action=action,
                    semantic_label=semantic_label,
                )
            )
        delta_obj = diff.get("delta_num_objects")
        if delta_obj is not None and int(delta_obj) < 0:
            signals.append(
                ProgressSignal(
                    signal_id=self._next_id(),
                    episode_id=episode_id,
                    step=step,
                    signal_type="token_progress",
                    magnitude=float(-int(delta_obj)),
                    state_hash=state_hash,
                    action=action,
                    semantic_label=semantic_label,
                    metadata={"delta_num_objects": delta_obj},
                )
            )
        return signals
