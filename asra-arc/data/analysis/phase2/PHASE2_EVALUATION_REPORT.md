# Phase 2 Full-Dataset Evaluation — Original ARC

**Date:** 2026-06-01  
**Pipeline:** `asra.perception.BeforeAfterAnalyzer` + `RuleCandidateGenerator`  
**Corpus:** [fchollet/ARC](https://github.com/fchollet/ARC) (`data/arc/original/`)

---

## Run configuration

| Split | Tasks | Reports | Wall time |
|-------|-------|---------|-----------|
| Training | 400 | `reports/training/*.json` | ~14 s |
| Evaluation | 400 | `reports/evaluation/*.json` | ~46 s |
| **Total** | **800** | 800 JSON files (~87 MB) | **~60 s** |

Each report: object extraction → region annotation → transform detection → rule candidates per task.

---

## Summary metrics

### Training (400 tasks)

| Metric | Value |
|--------|-------|
| Tasks with rule candidates | 400 / 400 (100%) |
| Tasks with full-demo common rule (confidence 1.0) | 392 / 400 (**98.0%**) |
| Avg objects per input scene | **13.16** |
| Avg transform events per demo pair | **16.86** |

**Transform events (aggregate):**

| Class | Count |
|-------|-------|
| DELETE | 6,588 |
| ROTATE | 5,065 |
| CREATE | 4,821 |
| IDENTITY | 3,334 |
| TRANSLATE | 2,146 |

### Evaluation (400 tasks)

| Metric | Value |
|--------|-------|
| Tasks with rule candidates | 400 / 400 (100%) |
| Tasks with full-demo common rule (confidence 1.0) | 391 / 400 (**97.75%**) |
| Avg objects per input scene | **25.40** |
| Avg transform events per demo pair | **30.90** |

**Transform events (aggregate):**

| Class | Count |
|-------|-------|
| ROTATE | 11,768 |
| DELETE | 11,444 |
| CREATE | 7,492 |
| IDENTITY | 6,332 |
| TRANSLATE | 5,074 |

---

## Interpretation

1. **Coverage:** Every task produced at least one rule candidate; ~98% share a single transform pattern across all training demos in the heuristic generator (high **structural regularity** in demo pairs, not ARC test accuracy).

2. **Complexity:** Evaluation grids yield ~2× more objects and transform events than training — consistent with harder/larger held-out tasks in the ARC split.

3. **Event mix:** DELETE / CREATE / ROTATE dominate — expected for object-centric differencing when object matching is greedy; many tasks recompose objects rather than purely translate.

4. **Limitations (Phase 2 baseline):**
   - No test-output solving; metrics are **perception + demo consistency** only.
   - RECOLOR / REFLECT under-reported (often folded into ROTATE/IDENTITY via shape_hash).
   - 8–9 tasks per split lack perfect cross-demo rule agreement — worth manual inspection in `reports/*/`.

---

## Sample tasks to inspect (low common-rule confidence)

Regenerate list:

```bash
python scripts/eval_phase2_batch.py --report-dir data/analysis/phase2/reports/training --list-exceptions
```

(Use reports where top `rule_candidates[0].confidence` < 1.0)

---

## Artifacts

| Path | Description |
|------|-------------|
| `data/analysis/phase2/summary_training.json` | Aggregated training metrics |
| `data/analysis/phase2/summary_evaluation.json` | Aggregated evaluation metrics |
| `data/analysis/phase2/reports/training/` | Per-task JSON (400) |
| `data/analysis/phase2/reports/evaluation/` | Per-task JSON (400) |

---

## Next steps

1. Spot-check exception tasks (8 training, 9 evaluation without confidence-1.0 common rule).
2. Integrate object scenes into Phase 1 transition exports (`--object-scenes`).
3. Optional: ARCLE single-action validation for transform labels.
4. Phase 3: exploration / memory on MiniGrid using object features.
