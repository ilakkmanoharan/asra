from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from asra.decision_biology.state_hash import hash_biology_state


@dataclass
class PathwayState:
    gene_activities: dict[str, float]
    pathway_id: str = "omnipath_signaling"

    def to_dict(self) -> dict[str, Any]:
        h = hash_biology_state(self.gene_activities, self.pathway_id)
        return {
            "domain": "decision_biology",
            "pathway_id": self.pathway_id,
            "gene_activities": dict(self.gene_activities),
            "state_hash": h,
            "state_type": "gene_activity_vector",
        }


@dataclass
class PathwaySimulator:
    """Perturbation environment with OmniPath prior as adjacency for one-step propagation."""

    genes: list[str]
    edges: list[tuple[str, str]]
    prior_weights: dict[tuple[str, str], float] = field(default_factory=dict)
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self) -> None:
        if not self.prior_weights:
            for u, v in self.edges:
                self.prior_weights[(u, v)] = 1.0

    @classmethod
    def from_subgraph(cls, genes: list[str], edges: list[tuple[str, str]], seed: int = 0) -> "PathwaySimulator":
        sim = cls(genes=genes, edges=edges, rng=random.Random(seed))
        return sim

    def random_initial_state(self) -> PathwayState:
        acts = {g: 1.0 if self.rng.random() > 0.65 else 0.0 for g in self.genes}
        # Ensure at least one receptor/ligand on
        if self.genes and sum(acts.values()) == 0:
            acts[self.genes[0]] = 1.0
        return PathwayState(acts)

    def available_actions(self) -> list[str]:
        return [f"knockdown_{g}" for g in self.genes] + [f"activate_{g}" for g in self.genes]

    def _propagate(self, acts: dict[str, float]) -> dict[str, float]:
        out = dict(acts)
        for source, target in self.edges:
            w = self.prior_weights.get((source, target), 0.0)
            if acts.get(source, 0.0) >= 0.5 and w > 0:
                out[target] = min(1.0, out.get(target, 0.0) + 0.35 * w)
        return {g: 1.0 if out[g] >= 0.5 else 0.0 for g in self.genes}

    def prior_predict(self, state: PathwayState, action: str) -> PathwayState:
        """One-step prediction using prior only (no learned residual)."""
        acts = dict(state.gene_activities)
        if action.startswith("knockdown_"):
            g = action.replace("knockdown_", "", 1)
            acts[g] = 0.0
        elif action.startswith("activate_"):
            g = action.replace("activate_", "", 1)
            acts[g] = 1.0
        return PathwayState(self._propagate(acts))

    def step(self, state: PathwayState, action: str) -> tuple[PathwayState, dict[str, Any]]:
        before = dict(state.gene_activities)
        nxt = self.prior_predict(state, action)
        after = nxt.gene_activities
        changed = [g for g in self.genes if before.get(g) != after.get(g)]
        diff = {
            "num_changed_genes": len(changed),
            "changed_genes": changed,
            "change_ratio": len(changed) / max(len(self.genes), 1),
        }
        return nxt, diff

    def make_transition(
        self,
        episode_id: str,
        step_index: int,
        state: PathwayState,
        action: str,
        next_state: PathwayState,
        diff: dict[str, Any],
    ) -> dict[str, Any]:
        pred = self.prior_predict(state, action)
        pred_match = pred.gene_activities == next_state.gene_activities
        return {
            "transition_id": str(uuid4()),
            "episode_id": episode_id,
            "game_id": "decision_biology",
            "level_id": "omnipath_signaling_v0",
            "step_index": step_index,
            "state": state.to_dict(),
            "action": {"name": action, "index": self.available_actions().index(action)},
            "next_state": next_state.to_dict(),
            "reward": float(len(diff.get("changed_genes", []))),
            "terminal_state": step_index >= 49,
            "diff": diff,
            "metadata": {
                "domain": "decision_biology",
                "dataset": "omnipath_prior",
                "prior_predict_match": pred_match,
                "raw_action_semantics_known": False,
            },
        }
