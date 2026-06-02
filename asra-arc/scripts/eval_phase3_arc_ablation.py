#!/usr/bin/env python3
"""Ablation: Phase 1 baseline vs Phase 3 exploration on ARC-AGI-3 mock/replay."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from asra.agent.baseline_agent import BaselineAgent
from asra.env.arc_agi3_runner import ArcAGI3Runner
from asra.env.backend_factory import create_backend
from asra.exploration.arc_exploration import ArcExplorationRunner


def _loop_count(transitions: list[dict[str, Any]]) -> int:
    recent: list[str] = []
    loops = 0
    for row in transitions:
        sh = row["state"]["state_hash"]
        if sh in recent:
            loops += 1
        recent.append(sh)
        recent = recent[-20:]
    return loops


def _unique_nodes(transitions: list[dict[str, Any]]) -> int:
    return len({row["state"]["state_hash"] for row in transitions} | {row["next_state"]["state_hash"] for row in transitions})


def run_baseline(data_dir: Path, max_steps: int, mock: bool, replay_file: str | None) -> dict[str, Any]:
    backend = create_backend(mock=mock, replay_file=replay_file, live=False)
    runner = ArcAGI3Runner(backend=backend, data_dir=str(data_dir / "baseline"))
    result = runner.run_episode(BaselineAgent(), max_steps=max_steps)
    return {
        "policy": "simple_exploration",
        "steps": len(result.transitions),
        "total_reward": result.total_reward,
        "final_status": result.final_status,
        "unique_nodes": _unique_nodes(result.transitions),
        "loop_count": _loop_count(result.transitions),
        "episode_id": result.episode_id,
    }


def run_phase3(data_dir: Path, max_steps: int, mock: bool, replay_file: str | None) -> dict[str, Any]:
    backend = create_backend(mock=mock, replay_file=replay_file, live=False)
    base = ArcAGI3Runner(backend=backend, data_dir=str(data_dir / "phase3"))
    result = ArcExplorationRunner(base, data_dir=str(data_dir / "phase3")).run_episode(max_steps=max_steps)
    return {
        "policy": result.policy,
        "steps": len(result.transitions),
        "total_reward": result.total_reward,
        "final_status": result.final_status,
        "unique_nodes": result.unique_nodes,
        "loop_count": result.loop_count,
        "episode_id": result.episode_id,
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Phase 3 ARC-AGI-3 ablation report")
    p.add_argument("--max-steps", type=int, default=50)
    p.add_argument("--mock", action="store_true", default=True)
    p.add_argument("--replay-file", default=None)
    p.add_argument("--output", default="data/analysis/phase3/arc_ablation.json")
    args = p.parse_args()

    data_dir = Path("data/arc_exploration/ablation")
    baseline = run_baseline(data_dir, args.max_steps, args.mock, args.replay_file)
    phase3 = run_phase3(data_dir, args.max_steps, args.mock, args.replay_file)

    report = {
        "max_steps": args.max_steps,
        "baseline": baseline,
        "phase3": phase3,
        "phase3_more_unique_nodes": phase3["unique_nodes"] >= baseline["unique_nodes"],
        "phase3_fewer_loops": phase3["loop_count"] <= baseline["loop_count"],
        "non_regression_reward": phase3["total_reward"] >= baseline["total_reward"],
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
