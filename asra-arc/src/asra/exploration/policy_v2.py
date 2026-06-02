from __future__ import annotations

from typing import Any

from asra.exploration.exploration_graph import ExplorationGraph
from asra.exploration.novelty import NoveltyScorer
from asra.exploration.schemas import SubgoalState
from asra.exploration.strategies import StrategyLibrary
from asra.exploration.usefulness import UsefulnessScorer
from asra.exploration.visitation_memory import VisitationMemory


class ExplorationPolicyV2:
    name = "exploration_v2"

    def __init__(
        self,
        novelty: NoveltyScorer | None = None,
        usefulness: UsefulnessScorer | None = None,
        strategy_library: StrategyLibrary | None = None,
        strategy_weight: float = 0.4,
    ) -> None:
        self.novelty = novelty or NoveltyScorer()
        self.usefulness = usefulness or UsefulnessScorer()
        self.strategies = strategy_library or StrategyLibrary()
        self.strategy_weight = strategy_weight
        self._edge_observations: dict[tuple[str, str], list[dict[str, Any]]] = {}

    def observe(self, transition: dict[str, Any]) -> None:
        key = (transition["state"]["state_hash"], transition["action"]["name"])
        self._edge_observations.setdefault(key, []).append(transition)

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
        if not available_actions:
            raise ValueError("No available actions")
        frontier = graph.frontier_score(state_hash)
        strategy_actions = self.strategies.bias_for_state(precondition or {}) if precondition else []

        scored: list[tuple[float, str, str]] = []
        for action in available_actions:
            obs_list = self._edge_observations.get((state_hash, action), [])
            if obs_list:
                avg_novelty = sum(
                    t.get("metadata", {}).get("exploration", {}).get("novelty", 0.0) for t in obs_list
                ) / len(obs_list)
                avg_use = sum(
                    t.get("metadata", {}).get("exploration", {}).get("usefulness", 0.0) for t in obs_list
                ) / len(obs_list)
                succ_hash = obs_list[-1]["next_state"]["state_hash"]
                repeat_penalty = 1.0 if memory.count_in_recent(succ_hash) > 1 else 0.0
                score = avg_novelty + avg_use - repeat_penalty
                reason = "observed_edge"
            else:
                pseudo_succ = f"{state_hash}:{action}"
                n = self.novelty.state_novelty(
                    pseudo_succ, memory, object_scene=object_scene, frontier_bonus=frontier
                )
                u = self.usefulness.score(subgoal=subgoal)
                score = n + u
                reason = "unexplored_edge"
            if action in strategy_actions:
                score += self.strategy_weight
                reason = "strategy_bias"
            if memory.count_in_recent(state_hash) > 2 and action == available_actions[0]:
                score -= 0.2
            scored.append((score, action, reason))

        score, action, reason = max(scored, key=lambda item: item[0])
        strategy_hint = self.strategies.strategy_hint(precondition or {}) if precondition else None
        return {
            "selected_action": action,
            "reason": reason,
            "score": score,
            "strategy_hint": strategy_hint if reason == "strategy_bias" else None,
        }
