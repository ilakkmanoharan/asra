from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from asra.causality.arc_semantics import eval_prediction_mae, iter_transitions_jsonl
from asra.causality.effect_summarizer import ActionEffectSummarizer
from asra.causality.hypothesis_tester import HypothesisTester
from asra.causality.uncertainty import UncertaintyScorer


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate Phase 4 ARC semantics on transition logs")
    parser.add_argument("--input-dir", default="data/transitions")
    parser.add_argument("--output", default="data/analysis/phase4/arc_semantics_eval.json")
    args = parser.parse_args()

    metrics = eval_prediction_mae(args.input_dir)
    summarizer = ActionEffectSummarizer()
    tester = HypothesisTester()
    scorer = UncertaintyScorer()

    for transition in iter_transitions_jsonl(args.input_dir):
        summarizer.observe_transition(transition)

    signatures = summarizer.summarize_all()
    for sig in signatures:
        tester.upsert_from_signature(sig)

    metrics["signature_count"] = len(signatures)
    metrics["hypothesis_count"] = len(tester.all_hypotheses())
    metrics["mean_confidence"] = (
        sum(s.confidence for s in signatures) / len(signatures) if signatures else 0.0
    )
    metrics["mean_uncertainty"] = (
        sum(scorer.score(s) for s in signatures) / len(signatures) if signatures else 0.0
    )
    metrics["mean_consistency_rate"] = (
        sum(1 for s in signatures if s.confidence >= 0.5) / len(signatures) if signatures else 0.0
    )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
