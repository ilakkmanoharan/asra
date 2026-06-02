from __future__ import annotations

from pathlib import Path
from typing import Any

from asra.exploration.schemas import StrategyPattern


class StrategyLibrary:
    """Index of reusable action subsequences keyed by preconditions."""

    def __init__(self) -> None:
        self._strategies: dict[str, StrategyPattern] = {}

    def add(self, pattern: StrategyPattern) -> None:
        existing = self._strategies.get(pattern.strategy_id)
        if existing:
            existing.success_count += pattern.success_count
            if len(pattern.action_sequence) > len(existing.action_sequence):
                existing.action_sequence = list(pattern.action_sequence)
        else:
            self._strategies[pattern.strategy_id] = pattern

    def find_match(self, precondition: dict[str, Any]) -> StrategyPattern | None:
        best: StrategyPattern | None = None
        best_score = -1
        for pattern in self._strategies.values():
            score = _precondition_match_score(precondition, pattern.precondition)
            if score > best_score:
                best_score = score
                best = pattern
        return best if best_score > 0 else None

    def bias_for_state(self, precondition: dict[str, Any]) -> list[str]:
        match = self.find_match(precondition)
        if match and match.action_sequence:
            return [match.action_sequence[0]]
        return []

    def strategy_hint(self, precondition: dict[str, Any]) -> str | None:
        match = self.find_match(precondition)
        return match.strategy_id if match else None

    def extract_from_episode(
        self,
        transitions: list[dict[str, Any]],
        precondition: dict[str, Any],
        env_id: str,
        name: str = "door_key_sequence",
    ) -> StrategyPattern | None:
        if not transitions:
            return None
        success = any(t.get("next_state", {}).get("status") == "WIN" for t in transitions)
        if not success:
            return None
        actions = [t["action"]["name"] for t in transitions]
        compressed = _compress_action_sequence(actions)
        if not compressed:
            return None
        strategy_id = f"{name}_v{len(self._strategies) + 1}"
        pattern = StrategyPattern(
            strategy_id=strategy_id,
            name=name,
            precondition=dict(precondition),
            action_sequence=compressed,
            success_count=1,
            source_env=env_id,
        )
        self.add(pattern)
        return pattern

    def to_list(self) -> list[dict[str, Any]]:
        return [p.to_dict() for p in self._strategies.values()]

    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(self.to_list(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> StrategyLibrary:
        lib = cls()
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for row in data:
            lib.add(StrategyPattern(**row))
        return lib


def _precondition_match_score(state: dict[str, Any], required: dict[str, Any]) -> int:
    score = 0
    for key, value in required.items():
        if state.get(key) == value:
            score += 1
        elif key in state:
            return -1
    return score


def _compress_action_sequence(actions: list[str]) -> list[str]:
    """Drop consecutive duplicate actions while preserving order."""
    out: list[str] = []
    for action in actions:
        if not out or out[-1] != action:
            out.append(action)
    return out


def default_doorkey_strategy() -> StrategyPattern:
    """Seed strategy for DoorKey when no successful episode yet."""
    return StrategyPattern(
        strategy_id="door_key_sequence_seed",
        name="door_key_sequence",
        precondition={"env_type": "doorkey", "has_key": False, "door_open": False},
        action_sequence=["ACTION3", "ACTION4", "ACTION3", "ACTION6", "ACTION3"],
        success_count=0,
        source_env="MiniGrid-DoorKey-8x8-v0",
    )
