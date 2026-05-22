#!/usr/bin/env python3
"""
Priority 3: large-scale transition generation (mock backend).

Default target: 10,000 episodes (per phase1-checks.md). Use --num-episodes to adjust.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from asra.agent.baseline_agent import BaselineAgent  # noqa: E402
from asra.env.arc_agi3_runner import ArcAGI3Runner  # noqa: E402
from asra.env.backend_factory import create_backend  # noqa: E402
from asra.export.dataset_exporter import export_dataset  # noqa: E402
from asra.memory.state_graph import build_graph_from_transition_dir  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-episodes", type=int, default=10_000)
    parser.add_argument("--max-steps", type=int, default=50)
    parser.add_argument("--data-dir", default="data/large_scale")
    parser.add_argument("--progress-every", type=int, default=500)
    parser.add_argument("--skip-export", action="store_true")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    agent = BaselineAgent()

    start = time.time()
    for i in range(args.num_episodes):
        runner = ArcAGI3Runner(
            backend=create_backend(mock=True),
            game_id=f"scale-game-{(i % 100):03d}",
            level_id=f"level-{(i % 10)}",
            data_dir=str(data_dir),
        )
        runner.run_episode(agent, args.max_steps)
        if (i + 1) % args.progress_every == 0:
            elapsed = time.time() - start
            print(f"episodes {i + 1}/{args.num_episodes} ({elapsed:.1f}s)")

    elapsed = time.time() - start
    print(f"Finished {args.num_episodes} episodes in {elapsed:.1f}s")

    if args.skip_export:
        return

    print("Exporting dataset...")
    paths = export_dataset(data_dir / "transitions", data_dir / "exports")
    print(paths)

    print("Building graph...")
    graph = build_graph_from_transition_dir(data_dir / "transitions")
    out = data_dir / "graphs" / "state_graph.json"
    graph.save(out)
    print(out)

    hash_script = _ROOT / "scripts" / "hash_stability_analysis.py"
    export_jsonl = data_dir / "exports" / "asra_v0_1_transitions.jsonl"
    if hash_script.is_file() and export_jsonl.is_file():
        subprocess.run(
            [sys.executable, str(hash_script), str(export_jsonl)],
            cwd=str(_ROOT),
            check=True,
        )


if __name__ == "__main__":
    main()
