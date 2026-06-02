#!/usr/bin/env python3
"""Benchmark Phase 3 exploration v2 vs Phase 1 baseline on DoorKey."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from asra.exploration.minigrid_runner import run_minigrid_baseline_batch, run_minigrid_batch
from asra.utils.serialization import read_jsonl


def _summarize_results(results: list[Any], transition_dir: Path) -> dict[str, Any]:
    episodes = len(results)
    successes = sum(1 for r in results if r.success)
    steps = [r.steps for r in results]
    success_steps = [r.steps for r in results if r.success]
    revisit_steps = 0
    total_steps = 0
    unique_hashes: set[str] = set()

    for path in transition_dir.glob("*.jsonl"):
        seen: set[str] = set()
        for row in read_jsonl(path):
            total_steps += 1
            sh = row["state"]["state_hash"]
            unique_hashes.add(sh)
            if sh in seen:
                revisit_steps += 1
            seen.add(sh)

    return {
        "episodes": episodes,
        "successes": successes,
        "success_rate": round(successes / episodes, 4) if episodes else 0.0,
        "mean_steps": round(sum(steps) / episodes, 2) if episodes else 0.0,
        "median_success_steps": sorted(success_steps)[len(success_steps) // 2] if success_steps else None,
        "revisit_rate": round(revisit_steps / total_steps, 4) if total_steps else 0.0,
        "unique_nodes": len(unique_hashes),
        "strategy_reuse_episodes": sum(1 for r in results if getattr(r, "strategy_reused", False)),
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Phase 3 DoorKey benchmark: v2 vs Phase 1 baseline")
    p.add_argument("--env", default="MiniGrid-DoorKey-8x8-v0")
    p.add_argument("--episodes", type=int, default=20)
    p.add_argument("--max-steps", type=int, default=300)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--output", default="data/analysis/phase3/doorkey_benchmark.json")
    args = p.parse_args()

    v2_dir = Path("data/minigrid/doorkey_v2")
    baseline_dir = Path("data/minigrid/doorkey_baseline")

    v2_results = run_minigrid_batch(
        args.env,
        episodes=args.episodes,
        max_steps=args.max_steps,
        data_dir=str(v2_dir),
        seed=args.seed,
        export_replay_path=v2_dir / "replay" / "top_transitions.jsonl",
    )
    baseline_results = run_minigrid_baseline_batch(
        args.env,
        episodes=args.episodes,
        max_steps=args.max_steps,
        data_dir=str(baseline_dir),
        seed=args.seed,
    )

    v2_summary = _summarize_results(v2_results, v2_dir / "transitions")
    baseline_summary = _summarize_results(baseline_results, baseline_dir / "transitions")

    report = {
        "env_id": args.env,
        "episodes": args.episodes,
        "max_steps": args.max_steps,
        "phase3_v2": v2_summary,
        "phase1_baseline": baseline_summary,
        "v2_beats_baseline_success": v2_summary["success_rate"] > baseline_summary["success_rate"],
        "v2_lower_revisit_rate": v2_summary["revisit_rate"] < baseline_summary["revisit_rate"],
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
