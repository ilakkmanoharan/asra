#!/usr/bin/env python3
"""Evaluate Phase 5 goal inference on transition logs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from asra.goals import eval_goals_on_transitions  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="Evaluate ASRA Phase 5 goals")
    p.add_argument("--input-dir", default="data/transitions")
    p.add_argument("--output", default="data/analysis/phase5/arc_goals_eval.json")
    args = p.parse_args()
    metrics = eval_goals_on_transitions(args.input_dir)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
