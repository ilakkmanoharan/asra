#!/usr/bin/env python3
"""Summarize Phase 3 MiniGrid transition logs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from asra.exploration.exploration_graph import build_exploration_graph_from_transitions
from asra.utils.serialization import read_jsonl


def summarize_transitions(transition_dir: Path) -> dict[str, Any]:
    paths = sorted(transition_dir.glob("*.jsonl"))
    episodes = len(paths)
    steps = 0
    successes = 0
    total_reward = 0.0
    revisit_steps = 0
    novel_steps = 0

    for path in paths:
        episode_success = False
        seen_hashes: set[str] = set()
        for row in read_jsonl(path):
            steps += 1
            total_reward += float(row.get("reward", 0.0))
            sh = row["state"]["state_hash"]
            if sh in seen_hashes:
                revisit_steps += 1
            else:
                novel_steps += 1
            seen_hashes.add(sh)
            if row.get("next_state", {}).get("status") == "WIN":
                episode_success = True
        if episode_success:
            successes += 1

    graph = build_exploration_graph_from_transitions(transition_dir)
    return {
        "episodes": episodes,
        "steps": steps,
        "successes": successes,
        "success_rate": round(successes / episodes, 4) if episodes else 0.0,
        "total_reward": round(total_reward, 4),
        "revisit_rate": round(revisit_steps / steps, 4) if steps else 0.0,
        "novel_step_rate": round(novel_steps / steps, 4) if steps else 0.0,
        "unique_nodes": graph.unique_nodes(),
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Evaluate Phase 3 MiniGrid logs")
    p.add_argument("--transition-dir", default="data/minigrid/transitions")
    p.add_argument("--output", default="data/analysis/phase3/minigrid_summary.json")
    args = p.parse_args()

    summary = summarize_transitions(Path(args.transition_dir))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
