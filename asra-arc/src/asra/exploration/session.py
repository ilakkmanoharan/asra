from __future__ import annotations

from dataclasses import dataclass

from asra.exploration.exploration_graph import ExplorationGraph
from asra.exploration.replay import TransitionReplayBuffer
from asra.exploration.strategies import StrategyLibrary
from asra.exploration.visitation_memory import VisitationMemory


@dataclass
class ExplorationSessionState:
    """Cross-episode memory for strategy reuse and visit tracking."""

    memory: VisitationMemory
    graph: ExplorationGraph
    strategies: StrategyLibrary
    replay: TransitionReplayBuffer

    @classmethod
    def fresh(cls, replay_capacity: int = 500) -> ExplorationSessionState:
        return cls(
            memory=VisitationMemory(),
            graph=ExplorationGraph(),
            strategies=StrategyLibrary(),
            replay=TransitionReplayBuffer(capacity=replay_capacity),
        )
