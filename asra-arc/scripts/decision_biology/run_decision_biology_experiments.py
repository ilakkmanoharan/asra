#!/usr/bin/env python3
"""Run OmniPath + LINCS Decision Biology experiments for Patterns v5."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from asra.decision_biology.experiment import run_omnipath_prior_experiment
from asra.decision_biology.lincs_experiment import run_lincs_experiment


def main() -> None:
    base = ROOT / "data" / "decision_biology"
    omni = run_omnipath_prior_experiment(base / "omnipath", num_episodes=40, max_steps=25, seed=42)
    print("OmniPath:", omni["experiment_id"], "transitions", omni["num_transitions"])

    lincs = run_lincs_experiment(base / "lincs", cell_pattern="MCF7", max_signatures=100, max_genes=48)
    print("LINCS:", lincs["experiment_id"], "transitions", lincs["num_transitions"])

    combined = {
        "omnipath": omni,
        "lincs": lincs,
    }
    from asra.utils.serialization import write_json

    out = base / "analysis" / "decision_biology_combined_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, combined)
    print("Wrote", out)


if __name__ == "__main__":
    main()
