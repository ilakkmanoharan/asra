# Phase 2 exception tasks (17 total)

Historically **8 training + 9 evaluation** tasks had top `PER_OBJECT_*` confidence &lt; 1.0 (mixed demos).

| Split | Count | Detail report |
|-------|-------|----------------|
| Training | 8 | [EXCEPTIONS_TRAINING.md](EXCEPTIONS_TRAINING.md) |
| Evaluation | 9 | [EXCEPTIONS_EVALUATION.md](EXCEPTIONS_EVALUATION.md) |

## Resolution (2026-06-01)

`RuleCandidateGenerator` now emits **`BRANCHED_PER_DEMO`** (confidence 1.0) plus **`PER_DEMO_{i}_...`** rules when demos disagree. Re-run batch reports to refresh summaries; these 17 tasks should show branched top rules.

## Findings (root cause)

1. Mixed transform patterns across train demos (not parse failures).
2. **Dominant cause:** `mixed_transform_types_across_demos`.
3. **Phase 2B:** apply per-demo branches at solve time; Kaggle agent uses compact object hints only.

## Regenerate

```bash
cd asra-arc
python scripts/inspect_phase2_exceptions.py \
  --report-dir data/analysis/phase2/reports/training \
  --summary-json data/analysis/phase2/summary_training.json \
  --output-md data/analysis/phase2/EXCEPTIONS_TRAINING.md --label training
python scripts/inspect_phase2_exceptions.py \
  --report-dir data/analysis/phase2/reports/evaluation \
  --summary-json data/analysis/phase2/summary_evaluation.json \
  --output-md data/analysis/phase2/EXCEPTIONS_EVALUATION.md --label evaluation
```

Machine-readable: `exceptions_training.json`, `exceptions_evaluation.json`.
