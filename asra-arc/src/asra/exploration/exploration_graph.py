from __future__ import annotations

from pathlib import Path
from typing import Any

from asra.exploration.schemas import ExplorationEdge, ExplorationNode
from asra.utils.serialization import read_jsonl, write_json


class ExplorationGraph:
    """Exploration-centric state graph with visit counts and frontier scores."""

    def __init__(self) -> None:
        self.nodes: dict[str, ExplorationNode] = {}
        self._edges: dict[tuple[str, str, str], ExplorationEdge] = {}

    def add_transition(
        self,
        transition: dict[str, Any],
        step: int = 0,
        novelty_gain: float = 0.0,
        usefulness: float = 0.0,
        dead_end: bool = False,
    ) -> None:
        state = transition["state"]
        next_state = transition["next_state"]
        from_hash = state["state_hash"]
        to_hash = next_state["state_hash"]
        action = transition["action"]["name"]
        reward = float(transition.get("reward", 0.0))

        self._touch_node(from_hash, state, step, terminal=state.get("status") in {"WIN", "GAME_OVER"})
        self._touch_node(to_hash, next_state, step + 1, terminal=bool(transition.get("terminal_state")))

        key = (from_hash, to_hash, action)
        edge = self._edges.get(key)
        if edge is None:
            edge = ExplorationEdge(from_id=from_hash, to_id=to_hash, action=action, dead_end=dead_end)
            self._edges[key] = edge
        edge.count += 1
        edge._reward_sum += reward
        edge._novelty_sum += novelty_gain
        edge.avg_reward = edge._reward_sum / edge.count
        edge.avg_novelty_gain = edge._novelty_sum / edge.count
        edge.usefulness_score = (edge.usefulness_score * (edge.count - 1) + usefulness) / edge.count
        edge.dead_end = edge.dead_end or dead_end
        self._update_frontier_scores()

    def _touch_node(self, node_id: str, state: dict[str, Any], step: int, terminal: bool) -> None:
        grid = state.get("grid") or []
        shape = (len(grid), len(grid[0]) if grid else 0)
        scene = state.get("object_scene")
        node = self.nodes.get(node_id)
        if node is None:
            self.nodes[node_id] = ExplorationNode(
                node_id=node_id,
                state_hash=node_id,
                visit_count=1,
                first_seen_step=step,
                last_seen_step=step,
                terminal=terminal,
                object_summary=scene,
                grid_shape=shape,
            )
        else:
            node.visit_count += 1
            node.last_seen_step = step
            node.terminal = node.terminal or terminal
            if scene and not node.object_summary:
                node.object_summary = scene

    def _update_frontier_scores(self) -> None:
        successor_visits: dict[str, list[int]] = {}
        for edge in self._edges.values():
            succ = self.nodes.get(edge.to_id)
            if succ:
                successor_visits.setdefault(edge.from_id, []).append(succ.visit_count)
        for node_id, node in self.nodes.items():
            visits = successor_visits.get(node_id, [])
            if not visits:
                node.frontier_score = 1.0 if node.visit_count >= 1 else 0.0
            else:
                low_visit = sum(1 for v in visits if v <= 1)
                node.frontier_score = low_visit / len(visits)

    def frontier_score(self, state_hash: str) -> float:
        node = self.nodes.get(state_hash)
        return node.frontier_score if node else 1.0

    def frontier_gain(self, from_hash: str, to_hash: str) -> float:
        to_node = self.nodes.get(to_hash)
        if to_node is None or to_node.visit_count <= 1:
            return 1.0
        from_node = self.nodes.get(from_hash)
        if from_node and to_node.visit_count < from_node.visit_count:
            return 0.5
        return 0.0

    def unique_nodes(self) -> int:
        return len(self.nodes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "edges": [e.to_dict() for e in self._edges.values()],
        }

    def save(self, path: str | Path) -> None:
        write_json(path, self.to_dict())

    @classmethod
    def from_transition_dir(cls, input_dir: str | Path) -> ExplorationGraph:
        graph = cls()
        step = 0
        for path in sorted(Path(input_dir).glob("*.jsonl")):
            for transition in read_jsonl(path):
                meta = transition.get("metadata", {}).get("exploration", {})
                graph.add_transition(
                    transition,
                    step=step,
                    novelty_gain=float(meta.get("novelty", 0.0)),
                    usefulness=float(meta.get("usefulness", 0.0)),
                    dead_end=bool(meta.get("dead_end", False)),
                )
                step += 1
        return graph


def build_exploration_graph_from_transitions(input_dir: str | Path) -> ExplorationGraph:
    return ExplorationGraph.from_transition_dir(input_dir)
