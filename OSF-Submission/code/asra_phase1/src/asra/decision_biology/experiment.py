from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from asra.decision_biology.biology_state_graph import BiologyStateGraph
from asra.decision_biology.omnipath_loader import load_signaling_subgraph
from asra.decision_biology.pathway_simulator import PathwaySimulator
from asra.utils.serialization import write_json, write_jsonl


def run_omnipath_prior_experiment(
    out_root: Path,
    *,
    num_episodes: int = 40,
    max_steps: int = 25,
    seed: int = 42,
) -> dict[str, Any]:
    out_root = Path(out_root)
    raw_dir = out_root / "raw"
    trans_dir = out_root / "transitions"
    export_dir = out_root / "exports"
    graph_dir = out_root / "graphs"
    analysis_dir = out_root / "analysis"
    for d in (raw_dir, trans_dir, export_dir, graph_dir, analysis_dir):
        d.mkdir(parents=True, exist_ok=True)

    genes, edges, load_meta = load_signaling_subgraph(cache_path=raw_dir / "signaling_interactions.parquet")
    sim = PathwaySimulator.from_subgraph(genes, edges, seed=seed)

    # M0 prior graph (static)
    prior_m0 = {
        "type": "pathway_prior",
        "dataset": "omnipath",
        "n_genes": len(genes),
        "n_edges": len(edges),
        "edges": [{"source": u, "target": v, "weight": sim.prior_weights.get((u, v), 1.0)} for u, v in edges],
        "metadata": load_meta,
    }
    write_json(graph_dir / "prior_world_model_m0.json", prior_m0)

    all_transitions: list[dict[str, Any]] = []
    action_counts: Counter[str] = Counter()
    prior_matches = 0
    semantics_by_action: dict[str, list[int]] = defaultdict(list)

    import random

    rng = random.Random(seed)
    for ep in range(num_episodes):
        episode_id = f"omnipath_ep_{ep:04d}"
        state = sim.random_initial_state()
        ep_path = trans_dir / f"{episode_id}.jsonl"
        rows: list[dict[str, Any]] = []
        for step in range(max_steps):
            action = rng.choice(sim.available_actions())
            nxt, diff = sim.step(state, action)
            row = sim.make_transition(episode_id, step, state, action, nxt, diff)
            rows.append(row)
            all_transitions.append(row)
            action_counts[action] += 1
            if row["metadata"]["prior_predict_match"]:
                prior_matches += 1
            semantics_by_action[action.split("_", 1)[0]].append(diff["num_changed_genes"])
            state = nxt
        write_jsonl(ep_path, rows)

    export_path = export_dir / "asra_db_omnipath_transitions.jsonl"
    write_jsonl(export_path, all_transitions)

    graph = BiologyStateGraph()
    for row in all_transitions:
        graph.add_transition(row)
    graph.save(graph_dir / "state_graph.json")

    # Action semantics summary: mean genes changed per action family
    semantics_summary = {}
    for family, vals in semantics_by_action.items():
        semantics_summary[family] = {
            "count": len(vals),
            "mean_changed_genes": sum(vals) / len(vals) if vals else 0.0,
        }

    unique_states = len(graph.nodes)
    learned_edges = len(graph.to_dict()["edges"])
    prior_edge_set = {(u, v) for u, v in edges}
    observed_pairs = {(e["from"], e["to"]) for e in graph.to_dict()["edges"]}

    report = {
        "experiment_id": "db-omnipath-prior-v0",
        "description": "OmniPath signaling subgraph as M0 prior; perturbations as ASRA actions; gene activity states.",
        "load_meta": load_meta,
        "num_episodes": num_episodes,
        "max_steps": max_steps,
        "num_transitions": len(all_transitions),
        "prior_m0": {"n_genes": len(genes), "n_edges": len(edges)},
        "learned_world_model": {
            "unique_states": unique_states,
            "transition_edges": learned_edges,
        },
        "prior_predict_match_rate": prior_matches / max(len(all_transitions), 1),
        "action_semantics_summary": semantics_summary,
        "top_actions": action_counts.most_common(8),
        "paths": {
            "transitions": str(export_path),
            "prior_m0": str(graph_dir / "prior_world_model_m0.json"),
            "state_graph": str(graph_dir / "state_graph.json"),
        },
    }
    write_json(analysis_dir / "omnipath_prior_report.json", report)
    return report


def write_results_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# OmniPath prior experiment results",
        "",
        f"**Experiment:** `{report['experiment_id']}`",
        "",
        "## Data source",
        f"- Source: `{report['load_meta'].get('source')}`",
        f"- Genes: {report['load_meta'].get('n_genes')}",
        f"- Prior edges (M₀): {report['prior_m0']['n_edges']}",
        "",
        "## ASRA artifacts",
        f"- Transitions logged: **{report['num_transitions']}**",
        f"- Unique states in graph: **{report['learned_world_model']['unique_states']}**",
        f"- Learned transition edges: **{report['learned_world_model']['transition_edges']}**",
        f"- Prior one-step predict match rate: **{report['prior_predict_match_rate']:.1%}**",
        "",
        "## Action semantics (families)",
    ]
    for fam, stats in report.get("action_semantics_summary", {}).items():
        lines.append(f"- `{fam}`: n={stats['count']}, mean Δgenes={stats['mean_changed_genes']:.2f}")
    lines.extend(["", "## Top actions", ""])
    for name, cnt in report.get("top_actions", []):
        lines.append(f"- {name}: {cnt}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
