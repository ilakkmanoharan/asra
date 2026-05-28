from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from asra.utils.serialization import read_jsonl, write_json


class StateGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self._edges: dict[tuple[str, str, str], dict[str, Any]] = {}

    def add_transition(self, transition: dict[str, Any]) -> None:
        state_hash = transition["state"]["state_hash"]
        next_hash = transition["next_state"]["state_hash"]
        self._add_node(state_hash, transition["state"], terminal=transition["state"].get("status") in {"WIN", "GAME_OVER"})
        self._add_node(next_hash, transition["next_state"], terminal=transition["terminal_state"])
        key = (state_hash, next_hash, transition["action"]["name"])
        edge = self._edges.setdefault(key, {
            "from": state_hash,
            "to": next_hash,
            "action": transition["action"]["name"],
            "count": 0,
            "reward_history": [],
            "terminal_outcomes": [],
            "diff_summary": {},
        })
        edge["count"] += 1
        edge["reward_history"].append(transition["reward"])
        if transition["terminal_state"]:
            edge["terminal_outcomes"].append(transition["next_state"].get("status"))
        edge["diff_summary"] = {
            "num_changed_cells": transition.get("diff", {}).get("num_changed_cells", 0),
            "change_ratio": transition.get("diff", {}).get("change_ratio", 0.0),
        }

    def _add_node(self, state_hash: str, state: dict[str, Any], terminal: bool) -> None:
        node = self.nodes.setdefault(state_hash, {"grid": state["grid"], "visit_count": 0, "terminal": terminal})
        node["visit_count"] += 1
        node["terminal"] = node["terminal"] or terminal

    def to_dict(self) -> dict[str, Any]:
        edges = []
        for edge in self._edges.values():
            rewards = edge.pop("reward_history", []) if False else edge["reward_history"]
            row = {k: v for k, v in edge.items() if k != "reward_history"}
            row["avg_reward"] = sum(rewards) / len(rewards) if rewards else 0.0
            edges.append(row)
        return {"nodes": self.nodes, "edges": edges}

    def save(self, path: str | Path) -> None:
        write_json(path, self.to_dict())
        self._save_graphml_if_available(Path(path))

    def _save_graphml_if_available(self, json_path: Path) -> None:
        try:
            import networkx as nx
        except ImportError:
            return
        graph = nx.MultiDiGraph()
        for node_id, node in self.nodes.items():
            graph.add_node(node_id, visit_count=node["visit_count"], terminal=node["terminal"])
        for edge in self.to_dict()["edges"]:
            graph.add_edge(edge["from"], edge["to"], action=edge["action"], count=edge["count"], avg_reward=edge["avg_reward"])
        nx.write_graphml(graph, json_path.with_suffix(".graphml"))


def build_graph_from_transition_dir(input_dir: str | Path) -> StateGraph:
    graph = StateGraph()
    for path in sorted(Path(input_dir).glob("*.jsonl")):
        for transition in read_jsonl(path):
            graph.add_transition(transition)
    return graph
