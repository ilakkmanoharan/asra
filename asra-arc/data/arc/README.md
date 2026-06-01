# ARC datasets (Phase 2)

## Original ARC (fchollet/ARC)

Cloned into `original/_repo`. Symlinks:

- `original/training` → 400 tasks
- `original/evaluation` → 400 tasks

**Refresh:**

```bash
git clone --depth 1 https://github.com/fchollet/ARC.git data/arc/original/_repo
ln -sf _repo/data/training data/arc/original/training
ln -sf _repo/data/evaluation data/arc/original/evaluation
```

**Regenerate Phase 2 reports:**

```bash
python scripts/run_phase2_arc_batch.py --arc-root data/arc/original/training \
  --output-dir data/analysis/phase2/reports/training
python scripts/run_phase2_arc_batch.py --arc-root data/arc/original/evaluation \
  --output-dir data/analysis/phase2/reports/evaluation
python scripts/eval_phase2_batch.py --report-dir data/analysis/phase2/reports/training \
  --output data/analysis/phase2/summary_training.json --label training
python scripts/eval_phase2_batch.py --report-dir data/analysis/phase2/reports/evaluation \
  --output data/analysis/phase2/summary_evaluation.json --label evaluation
```

See `data/analysis/phase2/PHASE2_EVALUATION_REPORT.md` for latest metrics.
