# ASRA Phase 2 — Original ARC Full-Dataset Evaluation Results

**Author:** Ilakkuvaselvi Manoharan  
**Affiliation:** Nature Foundation Models  
**Date:** May 2026  
**Status:** Published preprint (SciLayer Systems) v1  
**Repository copy:** `documents/evaluation/asra-phase-2-original-arc-evaluation-results.md`  
**SciLayer:** https://sci-layer.vercel.app/articles/asra-phase-2-original-arc-evaluation-results  
**Companion theory:** [Phase 2 preprint](https://sci-layer.vercel.app/articles/object-centric-adaptive-reasoning-asra-phase-2)

> **Purpose:** Empirical results for the ASRA Observation Engine on the Original ARC corpus (800 tasks). Reports object extraction coverage, transform-event distributions, cross-demo rule consistency, and exception analysis — complementing the Phase 2 conceptual preprint with reproducible benchmark numbers.

---

## Abstract

ASRA Phase 2 segments integer grids into object scenes, detects transform events between demonstration pairs, and induces rule candidates. We evaluate the full `BeforeAfterAnalyzer` + `RuleCandidateGenerator` pipeline on all 400 training and 400 evaluation tasks from [fchollet/ARC](https://github.com/fchollet/ARC). Every task produces rule candidates (100% coverage). Cross-demo common rules at confidence 1.0 appear in **98.0%** of training tasks and **97.75%** of evaluation tasks. Evaluation split grids yield approximately **2×** the object count and transform events of training — consistent with harder held-out tasks. Seventeen tasks initially lacked perfect cross-demo agreement; root cause analysis shows **mixed transform types across demos**, resolved by `BRANCHED_PER_DEMO` rule emission. These metrics measure **perception and demo consistency**, not ARC test-output solve rate.

---

## 1. Evaluation scope

| Dimension | Detail |
|-----------|--------|
| **Pipeline** | `asra.perception.BeforeAfterAnalyzer` → `RuleCandidateGenerator` |
| **Corpus** | Original ARC — 400 training + 400 evaluation tasks |
| **Run date** | 2026-06-01 |
| **Wall time** | ~60 s total (~14 s training, ~46 s evaluation) |
| **Output** | 800 per-task JSON reports (~87 MB) |

**What this eval measures:**

- Object scene extraction succeeds on every task
- Transform events are detected per demo pair
- Rule candidates summarize demo-pair consistency

**What this eval does not measure:**

- ARC test-set solve accuracy (no test outputs used)
- Interactive ARC-AGI-3 competition score
- End-to-end agent win rate

Phase 2 on Original ARC is a **supervised abstraction laboratory**; interactive deployment uses compact object-scene hints in Kaggle agents (see Phase 2 preprint §8).

---

## 2. Run configuration

```bash
cd asra-arc
python scripts/eval_phase2_batch.py --split training
python scripts/eval_phase2_batch.py --split evaluation
```

Each report includes: object extraction → region annotation → transform detection → rule candidates per task.

| Split | Tasks | Reports path | Wall time |
|-------|-------|--------------|-----------|
| Training | 400 | `data/analysis/phase2/reports/training/*.json` | ~14 s |
| Evaluation | 400 | `data/analysis/phase2/reports/evaluation/*.json` | ~46 s |
| **Total** | **800** | 800 JSON files | **~60 s** |

Aggregates: `data/analysis/phase2/summary_training.json`, `summary_evaluation.json`.

---

## 3. Summary metrics

### 3.1 Training split (400 tasks)

| Metric | Value |
|--------|-------|
| Tasks with rule candidates | 400 / 400 (**100%**) |
| Tasks with full-demo common rule (confidence 1.0) | 392 / 400 (**98.0%**) |
| Avg objects per input scene | **13.16** |
| Avg transform events per demo pair | **16.86** |
| Parse errors | **0** |

**Transform event distribution (aggregate):**

| Class | Count |
|-------|-------|
| DELETE | 6,588 |
| ROTATE | 5,065 |
| CREATE | 4,821 |
| IDENTITY | 3,334 |
| TRANSLATE | 2,146 |

### 3.2 Evaluation split (400 tasks)

| Metric | Value |
|--------|-------|
| Tasks with rule candidates | 400 / 400 (**100%**) |
| Tasks with full-demo common rule (confidence 1.0) | 391 / 400 (**97.75%**) |
| Avg objects per input scene | **25.40** |
| Avg transform events per demo pair | **30.90** |
| Parse errors | **0** |

**Transform event distribution (aggregate):**

| Class | Count |
|-------|-------|
| ROTATE | 11,768 |
| DELETE | 11,444 |
| CREATE | 7,492 |
| IDENTITY | 6,332 |
| TRANSLATE | 5,074 |

### 3.3 Training vs evaluation comparison

| Metric | Training | Evaluation | Ratio (eval/train) |
|--------|----------|------------|-------------------|
| Avg objects per scene | 13.16 | 25.40 | **1.93×** |
| Avg transform events / pair | 16.86 | 30.90 | **1.83×** |
| Common-rule coverage | 98.0% | 97.75% | ~equal |

Evaluation tasks are structurally richer — more objects and more per-pair events — while rule-candidate coverage remains near-identical.

---

## 4. Interpretation

### 4.1 Coverage

**100% rule-candidate coverage** indicates the perception pipeline never fails silently on the full ARC corpus. Every task yields at least one interpretable structural hypothesis from demonstration pairs.

**~98% common-rule coverage** (confidence 1.0 across all training demos) measures **structural regularity within tasks** — not puzzle-solving success. A task can have perfect demo consistency yet require compositional reasoning at test time.

### 4.2 Transform mix

DELETE, CREATE, and ROTATE dominate both splits. This is expected for greedy object matching and differencing: many ARC tasks recompose objects (delete + create) or rotate components rather than pure translation.

RECOLOR and REFLECT are under-reported in this baseline — often folded into ROTATE or IDENTITY via `shape_hash` equivalence. Future Phase 2 revisions should split these explicitly.

### 4.3 Complexity gradient

The ~2× object/event ratio on evaluation supports using Original ARC evaluation split as a **harder perception stress test** relative to training — useful for regression testing perception changes before ARC-AGI-3 integration.

---

## 5. Exception tasks (17 total)

Historically **8 training + 9 evaluation** tasks had top per-object rule confidence &lt; 1.0.

| Split | Exception count | Detail |
|-------|-----------------|--------|
| Training | 8 | `EXCEPTIONS_TRAINING.md` |
| Evaluation | 9 | `EXCEPTIONS_EVALUATION.md` |

**Root cause:** `mixed_transform_types_across_demos` — not parse failures. Demos within the same task follow different transform patterns; forcing a single global rule yields low confidence.

**Resolution (Phase 2B):** `RuleCandidateGenerator` emits:

- `BRANCHED_PER_DEMO` (confidence 1.0) when demos disagree
- `PER_DEMO_{i}_*` rules for each demonstration branch

**Training exception task IDs:** `22eb0ac0`, `67385a82`, `794b24be`, `9565186b`, `a740d043`, `aedd82e4`, `b1948b0a`, `cce03e0d`

Regenerate exception reports:

```bash
cd asra-arc
python scripts/inspect_phase2_exceptions.py \
  --report-dir data/analysis/phase2/reports/training \
  --summary-json data/analysis/phase2/summary_training.json \
  --output-md data/analysis/phase2/EXCEPTIONS_TRAINING.md --label training
```

Machine-readable: `exceptions_training.json`, `exceptions_evaluation.json`.

---

## 6. Implementation reference

| Module | Path |
|--------|------|
| Object extractor | `asra-arc/src/asra/perception/objects.py` |
| Transform detector | `asra-arc/src/asra/perception/transforms.py` |
| Rule generator | `asra-arc/src/asra/perception/rules.py` |
| Batch eval | `asra-arc/scripts/eval_phase2_batch.py` |
| Exception inspector | `asra-arc/scripts/inspect_phase2_exceptions.py` |

**CLI:** `python -m asra run-phase2`

**Integration with Phase 1:** object scenes optional in transition exports via `ASRA_OBJECT_SCENES=1` and `snapshot.py`.

---

## 7. Relation to ARC-AGI-3

| Context | Phase 2 role |
|---------|--------------|
| **Original ARC (this report)** | Full perception + rule induction on static demos |
| **ARC-AGI-3 Kaggle agent** | Compact `object_scene()` / `object_delta()` hints in template agent |
| **Competition score** | Not directly predicted by Original ARC metrics — see [Evaluation Report v0](../evaluation/asra-arc-agi-3-evaluation-report-v0.md) |

Object-centric hints bias interactive exploration when cell-level diffs are ambiguous; they do not replace transition logging (Phase 1).

---

## 8. Limitations

1. **No test-output solving** — metrics are perception + demo consistency only.
2. **Greedy object matching** — may mis-align objects on dense grids; affects event counts.
3. **Under-reported transform classes** — RECOLOR/REFLECT folded into other labels.
4. **Static corpus only** — no action semantics or multi-step episodes in this eval.
5. **Heuristic rule generator** — not a learned program synthesizer.

---

## 9. Artifacts

| Path | Description |
|------|-------------|
| `data/analysis/phase2/PHASE2_EVALUATION_REPORT.md` | Pipeline run summary (source) |
| `data/analysis/phase2/summary_training.json` | Aggregated training metrics |
| `data/analysis/phase2/summary_evaluation.json` | Aggregated evaluation metrics |
| `data/analysis/phase2/reports/training/` | Per-task JSON (400) |
| `data/analysis/phase2/reports/evaluation/` | Per-task JSON (400) |
| `data/analysis/phase2/EXCEPTIONS_REPORT.md` | Exception overview |

---

## 10. References

- [ASRA Phase 2 preprint — Object-Centric Reasoning](https://sci-layer.vercel.app/articles/object-centric-adaptive-reasoning-asra-phase-2)
- [ASRA Integrated Architecture](https://sci-layer.vercel.app/articles/asra-integrated-architecture)
- [Original ARC corpus](https://github.com/fchollet/ARC)
- Local theory companion: `kaggle-notebooks/phase2/asra-phase2-object-centric-reasoning.md`

---

## 11. One-line takeaway

**ASRA Phase 2 achieves 100% rule-candidate coverage and ~98% cross-demo rule consistency on all 800 Original ARC tasks**, with evaluation split showing ~2× structural complexity — establishing a reproducible perception baseline before interactive ARC-AGI-3 deployment.
