#!/usr/bin/env python3
"""Priority 2: visualize state graph (nodes, edges, terminals, visit counts)."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from asra.utils.serialization import read_jsonl  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", default="data/graphs/state_graph.json")
    parser.add_argument("--transitions", default="data/exports/asra_v0_1_transitions.jsonl")
    parser.add_argument("--out-dir", default="data/analysis/graph_viz")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    graph_path = Path(args.graph)
    payload = json.loads(graph_path.read_text(encoding="utf-8"))
    nodes = payload.get("nodes", {})
    edges = payload.get("edges", [])

    try:
        import matplotlib.pyplot as plt
        import networkx as nx
    except ImportError as exc:
        (out_dir / "visualization_skipped.txt").write_text(
            f"Install analysis extras: pip install -e '.[analysis]'\n{exc}", encoding="utf-8"
        )
        print("Skipped PNG (missing matplotlib/networkx)")
        return

    g = nx.MultiDiGraph()
    terminal_nodes = []
    for nid, data in nodes.items():
        g.add_node(nid, visit_count=data.get("visit_count", 0), terminal=data.get("terminal", False))
        if data.get("terminal"):
            terminal_nodes.append(nid)

    for edge in edges:
        g.add_edge(edge["from"], edge["to"], action=edge.get("action"), count=edge.get("count", 1))

    # Layout (sample if huge)
    node_list = list(g.nodes())
    if len(node_list) > 500:
        node_list = node_list[:500]
        g = g.subgraph(node_list).copy()

    pos = nx.spring_layout(g, seed=42, k=0.8)
    visits = [g.nodes[n].get("visit_count", 1) for n in g.nodes()]
    sizes = [max(80, min(800, v * 40)) for v in visits]
    colors = ["#E74C3C" if g.nodes[n].get("terminal") else "#3498DB" for n in g.nodes()]

    fig, ax = plt.subplots(figsize=(14, 10))
    nx.draw_networkx_edges(g, pos, ax=ax, alpha=0.25, arrows=True, arrowsize=8, edge_color="#7F8C8D")
    nx.draw_networkx_nodes(g, pos, ax=ax, node_size=sizes, node_color=colors, alpha=0.85)
    ax.set_title(f"ASRA State Graph ({len(nodes)} nodes, {len(edges)} edges) — red=terminal")
    ax.axis("off")
    fig.tight_layout()
    png_path = out_dir / "state_graph.png"
    fig.savefig(png_path, dpi=150)
    plt.close(fig)
    print(f"Wrote {png_path}")

    # Cycle / hub stats from transitions
    rows = read_jsonl(Path(args.transitions)) if Path(args.transitions).is_file() else []
    edge_pairs = Counter((r["state"]["state_hash"], r["next_state"]["state_hash"], r["action"]["name"]) for r in rows)
    cycles = sum(1 for (a, b, _) in edge_pairs if a == b)
    hubs = Counter(e["from"] for e in edges).most_common(10)

    report = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "terminal_node_count": len(terminal_nodes),
        "self_loop_transitions": cycles,
        "top_hub_states": [{"state_hash": h, "out_edges": c} for h, c in hubs],
    }
    report_path = out_dir / "graph_analysis.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
