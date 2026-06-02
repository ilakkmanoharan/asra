from __future__ import annotations

from typing import Any, Protocol

from asra.agent.exploration_policy import SimpleExplorationPolicy
from asra.exploration.exploration_graph import ExplorationGraph
from asra.exploration.schemas import SubgoalState
from asra.exploration.visitation_memory import VisitationMemory


class ExplorationAgent(Protocol):
    name: str

    def select_action(
        self,
        state_hash: str,
        available_actions: list[str],
        graph: ExplorationGraph,
        memory: VisitationMemory,
        subgoal: SubgoalState | None = None,
        object_scene: dict[str, Any] | None = None,
        precondition: dict[str, Any] | None = None,
    ) -> dict[str, Any]: ...

    def observe(self, transition: dict[str, Any]) -> None: ...


class Phase1PolicyAdapter:
    """Wrap Phase 1 SimpleExplorationPolicy for gym exploration runners."""

    name = "simple_exploration"

    def __init__(self) -> None:
        self._policy = SimpleExplorationPolicy()

    def select_action(
        self,
        state_hash: str,
        available_actions: list[str],
        graph: ExplorationGraph,
        memory: VisitationMemory,
        subgoal: SubgoalState | None = None,
        object_scene: dict[str, Any] | None = None,
        precondition: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        del graph, memory, subgoal, object_scene, precondition
        return self._policy.select_action(state_hash, available_actions, dead_end_score=0.0)

    def observe(self, transition: dict[str, Any]) -> None:
        self._policy.observe(transition)
