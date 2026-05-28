from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from uuid import uuid4

import numpy as np

from asra.decision_biology.biology_state_graph import BiologyStateGraph
from asra.decision_biology.lincs_loader import (
    list_signature_ids,
    load_landmark_expression,
    perturbation_name_from_cid,
)
from asra.decision_biology.state_hash import hash_biology_state
from asra.utils.serialization import write_json, write_jsonl


def _baseline_state(genes: list[str]) -> dict[str, float]:
    return {g: 0.0 for g in genes}


def _profile_to_state(genes: list[str], values: np.ndarray, top_k: int = 12) -> dict[str, float]:
    """Binarize profile by top-|LFC| landmark genes (sparse state for ASRA hashing)."""
    acts = {g: 0.0 for g in genes}
    vals = np.array([0.0 if np.isnan(v) else float(v) for v in values])
    if len(vals) == 0:
        return acts
    order = np.argsort(-np.abs(vals))[:top_k]
    for i in order:
        if vals[i] != 0:
            acts[genes[i]] = 1.0 if vals[i] > 0 else -1.0  # store sign; hash uses float
    # normalize -1 to 0 for hash stability (use 0/1 only)
    return {g: 1.0 if acts[g] > 0 else 0.0 for g in genes}


def _state_dict(gene_activities: dict[str, float], pathway_id: str) -> dict[str, Any]:
    return {
        "domain": "decision_biology",
        "pathway_id": pathway_id,
        "state_type": "lincs_landmark_lfc",
        "gene_activities": dict(gene_activities),
        "state_hash": hash_biology_state(gene_activities, pathway_id),
    }


def _diff(before: dict[str, float], after: dict[str, float], genes: list[str]) -> dict[str, Any]:
    changed = [g for g in genes if before.get(g) != after.get(g)]
    return {
        "num_changed_genes": len(changed),
        "changed_genes": changed[:32],
        "change_ratio": len(changed) / max(len(genes), 1),
    }


def run_lincs_experiment(
    out_root: Path,
    *,
    cell_pattern: str = "MCF7",
    max_signatures: int = 100,
    max_genes: int = 48,
    top_k_genes: int = 12,
) -> dict[str, Any]:
    out_root = Path(out_root)
    raw_dir = out_root / "raw"
    export_dir = out_root / "exports"
    graph_dir = out_root / "graphs"
    analysis_dir = out_root / "analysis"
    for d in (export_dir, graph_dir, analysis_dir):
        d.mkdir(parents=True, exist_ok=True)

    pathway_id = f"lincs_{cell_pattern.lower()}_24h"
    sig_ids, load_meta = list_signature_ids(raw_dir, cell_pattern=cell_pattern, max_signatures=max_signatures)
    genes, matrix, expr_meta = load_landmark_expression(sig_ids, raw_dir, max_genes=max_genes)

    baseline = _baseline_state(genes)
    s0 = _state_dict(baseline, pathway_id)

    transitions: list[dict[str, Any]] = []
    action_counts: Counter[str] = Counter()
    moa_proxy: dict[str, list[int]] = defaultdict(list)

    for cid in sig_ids:
        if cid not in matrix.columns:
            continue
        col = matrix[cid].values
        after_acts = _profile_to_state(genes, col, top_k=top_k_genes)
        s1 = _state_dict(after_acts, pathway_id)
        action_name = f"perturbation_{perturbation_name_from_cid(cid)}"
        diff = _diff(baseline, after_acts, genes)
        row = {
            "transition_id": str(uuid4()),
            "episode_id": "lincs_batch_0001",
            "game_id": "decision_biology",
            "level_id": pathway_id,
            "step_index": len(transitions),
            "state": s0,
            "action": {"name": action_name, "index": len(transitions)},
            "next_state": s1,
            "reward": float(diff["num_changed_genes"]),
            "terminal_state": False,
            "diff": diff,
            "metadata": {
                "domain": "decision_biology",
                "dataset": "lincs_l1000",
                "source": "GEO_GSE92742",
                "signature_id": cid,
                "cell_line": cell_pattern,
                "raw_action_semantics_known": False,
            },
        }
        transitions.append(row)
        action_counts[action_name] += 1
        moa_proxy["up" if diff["num_changed_genes"] > 5 else "mod"].append(diff["num_changed_genes"])

    write_jsonl(export_dir / "asra_db_lincs_transitions.jsonl", transitions)

    graph = BiologyStateGraph()
    for row in transitions:
        graph.add_transition(row)
    graph.save(graph_dir / "state_graph.json")

    mean_changed = (
        sum(t["diff"]["num_changed_genes"] for t in transitions) / len(transitions) if transitions else 0
    )
    report = {
        "experiment_id": "db-lincs-l1000-v0",
        "description": "LINCS L1000 Level-2 GEX delta (978 landmark genes) as perturbation transitions.",
        "load_meta": {**load_meta, **expr_meta},
        "num_transitions": len(transitions),
        "unique_perturbations": len(action_counts),
        "mean_changed_genes": mean_changed,
        "top_k_genes": top_k_genes,
        "learned_world_model": {
            "unique_states": len(graph.nodes),
            "transition_edges": len(graph.to_dict()["edges"]),
        },
        "top_perturbations": action_counts.most_common(10),
        "paths": {
            "transitions": str(export_dir / "asra_db_lincs_transitions.jsonl"),
            "state_graph": str(graph_dir / "state_graph.json"),
        },
    }
    write_json(analysis_dir / "lincs_experiment_report.json", report)
    return report
