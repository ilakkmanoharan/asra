from __future__ import annotations

from pathlib import Path
from typing import Any

from asra.utils.serialization import write_json


class BiologyStateGraph:
    """State graph for non-grid Decision Biology transitions (reuses ASRA edge schema)."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self._edges: dict[tuple[str, str, str], dict[str, Any]] = {}

    def add_transition(self, transition: dict[str, Any]) -> None:
        sh = transition["state"]["state_hash"]
        nh = transition["next_state"]["state_hash"]
        self._add_node(sh, transition["state"])
        self._add_node(nh, transition["next_state"])
        key = (sh, nh, transition["action"]["name"])
        edge = self._edges.setdefault(
            key,
            {
                "from": sh,
                "to": nh,
                "action": transition["action"]["name"],
                "count": 0,
                "reward_history": [],
                "diff_summary": {},
            },
        )
        edge["count"] += 1
        edge["reward_history"].append(transition["reward"])
        edge["diff_summary"] = {
            "num_changed_genes": transition.get("diff", {}).get("num_changed_genes", 0),
            "change_ratio": transition.get("diff", {}).get("change_ratio", 0.0),
        }

    def _add_node(self, state_hash: str, state: dict[str, Any]) -> None:
        node = self.nodes.setdefault(
            state_hash,
            {
                "pathway_id": state.get("pathway_id"),
                "gene_activities": state.get("gene_activities"),
                "visit_count": 0,
            },
        )
        node["visit_count"] += 1

    def to_dict(self) -> dict[str, Any]:
        edges = []
        for edge in self._edges.values():
            rewards = edge["reward_history"]
            row = {k: v for k, v in edge.items() if k != "reward_history"}
            row["avg_reward"] = sum(rewards) / len(rewards) if rewards else 0.0
            edges.append(row)
        return {"nodes": self.nodes, "edges": edges, "domain": "decision_biology"}

    def save(self, path: str | Path) -> None:
        write_json(path, self.to_dict())
