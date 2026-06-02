from __future__ import annotations

import re
from typing import Any

from asra.exploration.env_utils import agent_carrying_type, grid_has_open_door
from asra.exploration.schemas import SubgoalState


def parse_babyai_mission(mission: str) -> list[SubgoalState]:
    """Rule-based parser for common BabyAI mission strings (v1)."""
    mission = mission.strip().lower()
    subgoals: list[SubgoalState] = []

    if match := re.search(r"go to (?:the )?(?:(\w+) )?(\w+)", mission):
        color, obj = match.group(1), match.group(2)
        desc = f"GoTo({obj}" + (f", color={color}" if color else "") + ")"
        subgoals.append(SubgoalState(subgoal_id="goto_target", index=0, description=desc, status="active"))

    if "pick up" in mission or "pickup" in mission:
        subgoals.append(
            SubgoalState(subgoal_id="pickup", index=len(subgoals), description="Pickup()", status="pending")
        )

    if "open" in mission and "door" in mission:
        subgoals.append(
            SubgoalState(subgoal_id="open_door", index=len(subgoals), description="OpenDoor()", status="pending")
        )

    if not subgoals:
        subgoals.append(SubgoalState(subgoal_id="explore", index=0, description="Explore()", status="active"))

    if subgoals[0].status == "pending":
        subgoals[0].status = "active"
        subgoals[0].entered_at_step = 0
    elif subgoals[0].entered_at_step is None:
        subgoals[0].entered_at_step = 0
    return subgoals


def doorkey_subgoals() -> list[SubgoalState]:
    return [
        SubgoalState(subgoal_id="has_key", index=0, description="Pickup key", status="active", entered_at_step=0),
        SubgoalState(subgoal_id="door_open", index=1, description="Open door", status="pending"),
        SubgoalState(subgoal_id="at_goal", index=2, description="Reach goal", status="pending"),
    ]


def detect_minigrid_milestones(carrying: bool, door_open: bool, at_goal: bool) -> dict[str, bool]:
    return {"has_key_or_carrying": carrying, "door_open": door_open, "at_goal": at_goal}


class SubgoalDetector:
    """Track subgoal progress for BabyAI and MiniGrid DoorKey environments."""

    def __init__(self, subgoals: list[SubgoalState]) -> None:
        self.subgoals = [SubgoalState(**sg.to_dict()) for sg in subgoals]
        self._active_index = 0
        for i, sg in enumerate(self.subgoals):
            if sg.status == "active":
                self._active_index = i
                break

    @classmethod
    def from_mission(cls, mission: str) -> SubgoalDetector:
        return cls(parse_babyai_mission(mission))

    @classmethod
    def for_doorkey(cls) -> SubgoalDetector:
        return cls(doorkey_subgoals())

    def active_subgoal(self) -> SubgoalState | None:
        if self._active_index >= len(self.subgoals):
            return None
        return self.subgoals[self._active_index]

    def update(self, env: Any, step: int, terminated: bool = False, reward: float = 0.0) -> list[SubgoalState]:
        active = self.active_subgoal()
        if active is None:
            return self.subgoals
        if self._is_complete(env, active, terminated=terminated, reward=reward):
            active.status = "completed"
            active.completed_at_step = step
            self._active_index += 1
            if self._active_index < len(self.subgoals):
                nxt = self.subgoals[self._active_index]
                nxt.status = "active"
                nxt.entered_at_step = step
        return self.subgoals

    def oracle_complete(self, env: Any, subgoal_id: str) -> bool:
        dummy = SubgoalState(subgoal_id=subgoal_id, index=0, description="")
        return self._is_complete(env, dummy)

    def _is_complete(
        self,
        env: Any,
        subgoal: SubgoalState,
        terminated: bool = False,
        reward: float = 0.0,
    ) -> bool:
        sid = subgoal.subgoal_id
        if sid == "goto_target":
            return _babyai_goto_complete(env)
        if sid == "pickup":
            return agent_carrying_type(env) is not None
        if sid == "open_door":
            return grid_has_open_door(env)
        if sid == "has_key":
            return agent_carrying_type(env) == "key"
        if sid == "door_open":
            return grid_has_open_door(env)
        if sid == "at_goal":
            return terminated and reward > 0
        if sid == "explore":
            return False
        return False


def _babyai_goto_complete(env: Any) -> bool:
    unwrapped = env.unwrapped
    instr = getattr(unwrapped, "instrs", None)
    if instr is None:
        return False
    try:
        import numpy as np

        desc = getattr(instr, "desc", None)
        if desc is None:
            return False
        for pos in getattr(desc, "obj_poss", []):
            if np.array_equal(pos, unwrapped.front_pos):
                return True
    except Exception:
        return False
    return False
