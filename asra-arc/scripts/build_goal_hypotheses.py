#!/usr/bin/env python3
"""Build Phase 5 goal hypotheses from transition logs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from asra.goals import bootstrap_from_arc_tasks, build_goals_from_transitions  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="Build ASRA Phase 5 goal hypotheses")
    p.add_argument("--transitions-dir", default="data/transitions")
    p.add_argument("--output-dir", default="data/goals/arc")
    p.add_argument("--arc-tasks-dir", default=None, help="Optional Original ARC tasks for template priors")
    args = p.parse_args()
    result = build_goals_from_transitions(args.transitions_dir, args.output_dir)
    if args.arc_tasks_dir:
        priors = bootstrap_from_arc_tasks(args.arc_tasks_dir)
        result["arc_template_priors"] = len(priors)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
