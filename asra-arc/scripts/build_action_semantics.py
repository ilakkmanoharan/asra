from __future__ import annotations

import json
from pathlib import Path

from asra.causality.arc_semantics import build_semantics_from_transitions, eval_prediction_mae, iter_transitions_jsonl


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build action semantics from transition JSONL")
    parser.add_argument("--input-dir", default="data/transitions")
    parser.add_argument("--output-dir", default="data/causality/arc/semantics")
    parser.add_argument("--eval-only", action="store_true")
    args = parser.parse_args()
    if args.eval_only:
        metrics = eval_prediction_mae(args.input_dir)
        print(json.dumps(metrics, indent=2))
        return
    result = build_semantics_from_transitions(args.input_dir, args.output_dir)
    result["eval"] = eval_prediction_mae(args.input_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
