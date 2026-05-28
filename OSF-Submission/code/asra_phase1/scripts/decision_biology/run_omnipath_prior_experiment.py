#!/usr/bin/env python3
"""Run Decision Biology experiment: OmniPath prior → ASRA transitions + world model."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from asra.decision_biology.experiment import run_omnipath_prior_experiment, write_results_markdown


def main() -> None:
    out_root = ROOT / "data" / "decision_biology" / "omnipath"
    report = run_omnipath_prior_experiment(out_root, num_episodes=40, max_steps=25, seed=42)
    docs = ROOT.parent / "private" / "documents" / "phase2-decision-biology" / "omnipath"
    docs.mkdir(parents=True, exist_ok=True)
    write_results_markdown(report, docs / "results.md")
    print("Experiment complete:", report["experiment_id"])
    print("Transitions:", report["num_transitions"])
    print("Prior predict match:", f"{report['prior_predict_match_rate']:.1%}")
    print("Report:", out_root / "analysis" / "omnipath_prior_report.json")
    print("Results doc:", docs / "results.md")


if __name__ == "__main__":
    main()
