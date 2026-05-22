from __future__ import annotations

from typing import Any

from asra.env.arc_agi3_runner import MockArcAGI3Environment
from asra.env.live_backend import LiveArcAGI3Environment
from asra.env.replay_backend import ReplayArcAGI3Environment


def create_backend(
    *,
    mock: bool = True,
    replay_file: str | None = None,
    live: bool = False,
    terminal_demo: bool = False,
) -> Any:
    if live:
        return LiveArcAGI3Environment()
    if replay_file:
        return ReplayArcAGI3Environment(replay_file)
    env = MockArcAGI3Environment()
    if terminal_demo:
        env.scenario = "terminal_demo"
    return env
