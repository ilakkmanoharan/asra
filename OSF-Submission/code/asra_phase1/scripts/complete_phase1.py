#!/usr/bin/env python3
"""Run the full Phase 1 completion pipeline (episodes → export → graph → hash check)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPLAY = ROOT / "data" / "raw" / "sample_arc_agi3_replay.json"


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> None:
    py = sys.executable
    run([py, "scripts/generate_sample_replay.py"])
    run([py, "-m", "asra", "run-episode", "--mock", "--terminal-demo", "--max-steps", "12", "--game-id", "mock-terminal", "--level-id", "demo"])
    run([py, "-m", "asra", "run-episode", "--mock", "--max-steps", "30", "--game-id", "mock-game", "--level-id", "mock-level"])
    if REPLAY.is_file():
        run([py, "-m", "asra", "run-episode", "--replay-file", str(REPLAY), "--max-steps", "20"])
    run([py, "-m", "asra", "run-batch", "--mock", "--num-episodes", "3", "--max-steps", "30"])
    run([py, "-m", "asra", "export-dataset"])
    run([py, "-m", "asra", "build-graph"])
    run([py, "scripts/hash_stability_analysis.py", "data/exports/asra_v0_1_transitions.jsonl"])
    print("\nPhase 1 pipeline complete. See data/exports/ and data/analysis/hash_stability/")


if __name__ == "__main__":
    main()
