from __future__ import annotations

from asra.planning.bfs_planner import BFSPlanner
from asra.planning.strategy_library import StrategyLibrary


def test_bfs_finds_goal():
    bfs = BFSPlanner(max_depth=4)
    bfs.observe("s0", "ACTION1", "s1")
    bfs.observe("s1", "ACTION2", "goal")
    plan = bfs.plan("g", "s0", {"goal"})
    assert plan.success
    assert len(plan.steps) == 2


def test_strategy_match():
    lib = StrategyLibrary()
    s = lib.match("move_to_target")
    assert s.name == "reach_target"
    assert lib.score_action(s, "translate") > 0
