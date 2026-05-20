#!/usr/bin/env python3
"""
Hash stability analysis for ASRA Phase 1 transition JSONL exports.

Implements the workflow described in phase1_hash_stability_analysis_prompt.md
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

# Allow running without editable install
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from asra.utils.hashing import hash_state  # noqa: E402


def load_transitions(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def grid_fingerprint(grid: list[list[int]]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(row) for row in grid)


def verify_hash_stability(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Same grid (fingerprint) must map to exactly one logged state_hash."""
    fp_to_hashes: dict[tuple[tuple[int, ...], ...], set[str]] = defaultdict(set)
    for row in rows:
        for key in ("state", "next_state"):
            block = row.get(key) or {}
            grid = block.get("grid")
            if grid is None:
                continue
            fp = grid_fingerprint(grid)
            h = block.get("state_hash")
            if h:
                fp_to_hashes[fp].add(h)

    unstable: list[dict[str, Any]] = []
    for fp, hashes in fp_to_hashes.items():
        if len(hashes) > 1:
            unstable.append(
                {
                    "grid": [list(r) for r in fp],
                    "hashes_found": sorted(hashes),
                }
            )

    return {
        "fingerprint_count": len(fp_to_hashes),
        "unstable_grids": unstable,
        "unstable_count": len(unstable),
    }


def detect_hash_collisions(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Different grids that map to the same recomputed SHA-256 (grid+shape only)."""
    hash_to_fps: dict[str, set[tuple[tuple[int, ...], ...]]] = defaultdict(set)
    seen_fps: set[tuple[tuple[int, ...], ...]] = set()

    for row in rows:
        for key in ("state", "next_state"):
            block = row.get(key) or {}
            grid = block.get("grid")
            if grid is None:
                continue
            fp = grid_fingerprint(grid)
            if fp in seen_fps:
                continue
            seen_fps.add(fp)
            h = hash_state(grid, metadata=None)
            hash_to_fps[h].add(fp)

    collisions = {h: sorted([list(map(list, fp)) for fp in fps]) for h, fps in hash_to_fps.items() if len(fps) > 1}
    return {
        "unique_grids_recomputed": len(seen_fps),
        "collision_count": len(collisions),
        "collisions": collisions,
    }


def analyze_determinism(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """(state_hash, action) -> set of next_state_hash; non-deterministic if len > 1."""
    mapping: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in rows:
        sh = row.get("state_hash") or (row.get("state") or {}).get("state_hash")
        nh = row.get("next_state_hash") or (row.get("next_state") or {}).get("state_hash")
        action = (row.get("action") or {}).get("name")
        if sh and nh and action:
            mapping[(sh, action)].add(nh)

    nondet = {f"{k[0]}|{k[1]}": sorted(v) for k, v in mapping.items() if len(v) > 1}
    return {
        "unique_state_action_pairs": len(mapping),
        "nondeterministic_pairs": len(nondet),
        "nondeterministic_examples": dict(list(nondet.items())[:20]),
    }


def analyze_state_reuse(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    for row in rows:
        sh = row.get("state_hash") or (row.get("state") or {}).get("state_hash")
        nh = row.get("next_state_hash") or (row.get("next_state") or {}).get("state_hash")
        if sh:
            counts[sh] += 1
        if nh:
            counts[nh] += 1
    top = counts.most_common(30)
    return {"state_visit_counts": dict(counts), "top_states": top}


def build_transition_graph(rows: list[dict[str, Any]]) -> Any:
    import networkx as nx

    g = nx.MultiDiGraph()
    for row in rows:
        sh = row.get("state_hash") or (row.get("state") or {}).get("state_hash")
        nh = row.get("next_state_hash") or (row.get("next_state") or {}).get("state_hash")
        action = (row.get("action") or {}).get("name", "?")
        if not sh or not nh:
            continue
        g.add_edge(sh, nh, action=action, episode_id=row.get("episode_id"))
    return g


def visualize_statistics(
    rows: list[dict[str, Any]],
    state_reuse: dict[str, Any],
    out_dir: Path,
    graph: Any,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        (out_dir / "visualization_skipped.txt").write_text(
            "matplotlib is not installed. Run: pip install '.[analysis]'\n", encoding="utf-8"
        )
        return

    # Hash frequency: visits per state_hash
    visits = list((state_reuse.get("state_visit_counts") or {}).values())
    if visits:
        plt.figure(figsize=(10, 4))
        plt.hist(visits, bins=min(50, max(5, len(set(visits)))), color="steelblue", edgecolor="black")
        plt.xlabel("Visit count (state appears in state/next_state)")
        plt.ylabel("Number of state hashes")
        plt.title("State hash visit distribution")
        plt.tight_layout()
        plt.savefig(out_dir / "state_visit_histogram.png", dpi=150)
        plt.close()

    # Transition graph stats
    if graph is not None and graph.number_of_nodes() > 0:
        import networkx as nx

        deg = dict(graph.degree())
        vals = list(deg.values())
        plt.figure(figsize=(10, 4))
        plt.hist(vals, bins=min(30, max(5, len(set(vals)))), color="darkseagreen", edgecolor="black")
        plt.xlabel("Total degree (in + out)")
        plt.ylabel("Number of nodes")
        plt.title("Transition graph degree distribution")
        plt.tight_layout()
        plt.savefig(out_dir / "graph_degree_histogram.png", dpi=150)
        plt.close()

        # Simple layout (small graphs only)
        if graph.number_of_nodes() <= 80:
            pos = nx.spring_layout(graph, seed=42, k=0.35)
            plt.figure(figsize=(12, 10))
            nx.draw_networkx_nodes(graph, pos, node_size=120, node_color="lightblue")
            nx.draw_networkx_edges(graph, pos, arrows=True, alpha=0.35, width=0.5)
            plt.title("State transition graph (spring layout)")
            plt.axis("off")
            plt.tight_layout()
            plt.savefig(out_dir / "transition_graph.png", dpi=150)
            plt.close()


def recompute_matches_logged(rows: list[dict[str, Any]]) -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    for i, row in enumerate(rows):
        for key in ("state", "next_state"):
            block = row.get(key) or {}
            grid = block.get("grid")
            logged = block.get("state_hash")
            if grid is None or not logged:
                continue
            expected = hash_state(grid, metadata=None)
            if expected != logged:
                mismatches.append(
                    {
                        "row_index": i,
                        "block": key,
                        "logged_hash": logged,
                        "recomputed_hash": expected,
                    }
                )
    return {"mismatch_count": len(mismatches), "mismatches": mismatches[:50]}


def cycle_likelihood(rows: list[dict[str, Any]], top_n: int = 15) -> list[tuple[str, str, int]]:
    """Count repeated (from_hash, to_hash) edges."""
    edge_counts: Counter[tuple[str, str]] = Counter()
    for row in rows:
        sh = row.get("state_hash") or (row.get("state") or {}).get("state_hash")
        nh = row.get("next_state_hash") or (row.get("next_state") or {}).get("state_hash")
        if sh and nh:
            edge_counts[(sh, nh)] += 1
    return edge_counts.most_common(top_n)


def action_change_consistency(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Per ACTIONk: distribution of num_changed_cells from diff."""
    by_action: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        name = (row.get("action") or {}).get("name")
        if not name:
            continue
        n = (row.get("diff") or {}).get("num_changed_cells")
        if isinstance(n, int):
            by_action[name].append(n)
    summary: dict[str, Any] = {}
    for act, vals in by_action.items():
        summary[act] = {
            "count": len(vals),
            "mean_changed_cells": sum(vals) / len(vals) if vals else 0.0,
            "unique_values": sorted(set(vals)),
        }
    return summary


def write_report(
    path: Path,
    rows: list[dict[str, Any]],
    stability: dict[str, Any],
    collisions: dict[str, Any],
    determinism: dict[str, Any],
    state_reuse: dict[str, Any],
    recompute_check: dict[str, Any],
    top_edges: list[tuple[tuple[str, str], int]],
    action_summary: dict[str, Any],
) -> None:
    total_grids = 0
    for row in rows:
        for key in ("state", "next_state"):
            if (row.get(key) or {}).get("grid") is not None:
                total_grids += 1

    unique_hashes_logged: set[str] = set()
    for row in rows:
        for key in ("state", "next_state"):
            h = (row.get(key) or {}).get("state_hash")
            if h:
                unique_hashes_logged.add(h)

    lines = [
        "=" * 50,
        "HASH STABILITY REPORT",
        "=" * 50,
        "",
        f"Total transitions analyzed: {len(rows)}",
        f"Total grids analyzed (state + next_state): {total_grids}",
        f"Unique grid fingerprints: {stability['fingerprint_count']}",
        f"Unique hashes (logged in JSONL): {len(unique_hashes_logged)}",
        f"Recomputed unique grids: {collisions['unique_grids_recomputed']}",
        "",
        f"Unstable grids (same grid, multiple logged hashes): {stability['unstable_count']}",
        f"Hash collisions (different grids, same recomputed hash): {collisions['collision_count']}",
        f"Logged vs recomputed mismatches (metadata leakage in hash): {recompute_check['mismatch_count']}",
        f"Non-deterministic (state_hash, action) -> next_state_hash pairs: {determinism['nondeterministic_pairs']}",
        "",
    ]

    if stability["unstable_count"] or collisions["collision_count"] or recompute_check["mismatch_count"]:
        lines.append("RESULT:")
        lines.append("❌ Hash instability or collision issues DETECTED")
    else:
        lines.append("RESULT:")
        lines.append("✅ Hash stability PASSED (same grid → one logged hash; recomputed hash matches logged)")

    if stability["unstable_grids"]:
        lines.extend(["", "Unstable grid examples:", ""])
        for ex in stability["unstable_grids"][:5]:
            lines.append(json.dumps(ex, indent=2))

    if collisions["collisions"]:
        lines.extend(["", "Collision examples (truncated):", ""])
        for h, grids in list(collisions["collisions"].items())[:3]:
            lines.append(f"hash={h}")
            lines.append(json.dumps(grids, indent=2))

    lines.extend(
        [
            "",
            "Top repeated (from_hash -> to_hash) edges:",
            json.dumps([{"from": a, "to": b, "count": c} for (a, b), c in top_edges], indent=2),
            "",
            "ACTION → grid change summary:",
            json.dumps(action_summary, indent=2),
            "",
            "Determinism sample (first nondeterministic keys if any):",
            json.dumps(determinism.get("nondeterministic_examples"), indent=2),
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="ASRA hash stability analysis")
    parser.add_argument(
        "jsonl",
        nargs="?",
        default=str(_ROOT / "data" / "exports" / "asra_v0_1_transitions.jsonl"),
        help="Path to asra_v0_1_transitions.jsonl",
    )
    parser.add_argument(
        "--out-dir",
        default=str(_ROOT / "data" / "analysis" / "hash_stability"),
        help="Directory for report and artifacts",
    )
    args = parser.parse_args()
    input_path = Path(args.jsonl)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.is_file():
        print(f"Input not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    rows = load_transitions(input_path)
    stability = verify_hash_stability(rows)
    collisions = detect_hash_collisions(rows)
    determinism = analyze_determinism(rows)
    state_reuse = analyze_state_reuse(rows)
    recompute_check = recompute_matches_logged(rows)
    top_edges = cycle_likelihood(rows, top_n=20)
    action_summary = action_change_consistency(rows)

    write_report(
        out_dir / "hash_stability_report.txt",
        rows,
        stability,
        collisions,
        determinism,
        state_reuse,
        recompute_check,
        top_edges,
        action_summary,
    )

    unstable_path = out_dir / "unstable_grids.json"
    unstable_path.write_text(json.dumps(stability["unstable_grids"], indent=2), encoding="utf-8")

    # state_statistics.csv
    import csv

    stats_path = out_dir / "state_statistics.csv"
    counts = state_reuse.get("state_visit_counts") or {}
    sorted_states = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    with stats_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["state_hash", "visit_count"])
        for h, c in sorted_states:
            w.writerow([h, c])

    graph = None
    try:
        graph = build_transition_graph(rows)
    except ImportError:
        (out_dir / "transition_graph_skipped.txt").write_text(
            "networkx is not installed. Run: pip install '.[graph]' or '.[analysis]'\n", encoding="utf-8"
        )
    if graph is not None:
        try:
            import networkx as nx

            nx.write_graphml(graph, out_dir / "transition_graph.graphml")
        except Exception as e:
            (out_dir / "transition_graph.graphml.error").write_text(str(e), encoding="utf-8")

    visualize_statistics(rows, state_reuse, out_dir, graph)

    print(f"Wrote report to {out_dir / 'hash_stability_report.txt'}")
    print(f"Artifacts in {out_dir}")


if __name__ == "__main__":
    main()
