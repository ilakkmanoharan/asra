from __future__ import annotations

from collections import deque
from typing import Any

from asra.planning.schemas import Plan, PlanStep


class BFSPlanner:
    """Breadth-first over observed state transitions (lookup table)."""

    def __init__(self, max_depth: int = 6) -> None:
        self.max_depth = max_depth
        self.graph: dict[str, dict[str, str]] = {}

    def observe(self, state_hash: str, action: str, next_hash: str) -> None:
        self.graph.setdefault(state_hash, {})[action] = next_hash

    def plan(
        self,
        game_id: str,
        start: str,
        goal_states: set[str] | None = None,
        *,
        plan_id: str = "plan_bfs",
    ) -> Plan:
        goal_states = goal_states or set()
        if start in goal_states:
            return Plan(plan_id, game_id, start, None, [], "bfs", True)
        queue: deque[tuple[str, list[tuple[str, str]]]] = deque([(start, [])])
        visited = {start}
        while queue:
            state, path = queue.popleft()
            if len(path) >= self.max_depth:
                continue
            for action, nxt in self.graph.get(state, {}).items():
                if nxt in visited:
                    continue
                new_path = path + [(action, nxt)]
                if goal_states and nxt in goal_states:
                    steps = [
                        PlanStep(a, nh, 1.0, "bfs_goal") for a, nh in new_path
                    ]
                    return Plan(plan_id, game_id, start, None, steps, "bfs", True)
                visited.add(nxt)
                queue.append((nxt, new_path))
        best = []
        for state, path in [(start, [])]:
            edges = self.graph.get(state, {})
            if edges:
                action = next(iter(edges))
                best = [PlanStep(action, edges[action], 0.5, "bfs_partial")]
        return Plan(plan_id, game_id, start, None, best, "bfs", False)
