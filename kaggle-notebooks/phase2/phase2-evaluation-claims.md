# Phase 2 Original ARC Evaluation — Claims, Metrics, and Caveats

**Last verified:** June 2026  
**Pipeline:** `asra.perception.BeforeAfterAnalyzer` + `RuleCandidateGenerator`  
**Corpus:** [fchollet/ARC](https://github.com/fchollet/ARC) — 400 training + 400 evaluation tasks (**800 total**)  
**Canonical metrics (repo):** `asra-arc/data/analysis/phase2/summary_training.json`, `summary_evaluation.json`, `PHASE2_EVALUATION_REPORT.md`

This document clarifies what Phase 2 evaluation **does** and **does not** prove, so public descriptions (papers, READMEs, grant text) stay accurate.

---

## One-sentence summary

Phase 2 was batch-evaluated on all 800 Original ARC tasks: **every task received at least one rule candidate**; **~2% of tasks** show genuine cross-demo transform heterogeneity under our heuristic detector; **branched per-demo rules are implemented in code** but **committed batch JSON was generated before that generator change** unless reports are re-run.

---

## What is true

### 800 Original ARC tasks evaluated

| Split | Tasks | Per-task reports |
|-------|-------|------------------|
| Training | 400 | `asra-arc/data/analysis/phase2/reports/training/{task_id}.json` |
| Evaluation | 400 | `asra-arc/data/analysis/phase2/reports/evaluation/{task_id}.json` |

Each report runs: object extraction → region annotation → transform detection → rule candidate ranking.

### 100% rule-candidate coverage

From committed summaries:

| Split | `num_with_rule_candidates` | `pct_with_rule_candidates` |
|-------|----------------------------|----------------------------|
| Training | 400 / 400 | **100%** |
| Evaluation | 400 / 400 | **100%** |

**Meaning:** The perception stack never returned an empty rule list on a parsed task. It does **not** mean the top rule is correct, complete, or sufficient to solve the task’s test input.

### ~2% cross-demo operator heterogeneity

Under the **pre-branch** metric — top global rule has `confidence < 1.0` because demos disagree on transform-type sets:

| Split | Exception count | Rate |
|-------|-----------------|------|
| Training | 8 | 2.0% |
| Evaluation | 9 | 2.25% |
| **Total** | **17** | **2.1%** |

Training exception IDs (committed): `22eb0ac0`, `67385a82`, `794b24be`, `9565186b`, `a740d043`, `aedd82e4`, `b1948b0a`, `cce03e0d`.

Detail: `asra-arc/data/analysis/phase2/EXCEPTIONS_REPORT.md`, `EXCEPTIONS_TRAINING.md`, `EXCEPTIONS_EVALUATION.md`.

**Root cause (not parse failure):** Mixed transform patterns across train demos — e.g. one demo summarized as mostly `IDENTITY`, another as `CREATE`/`DELETE`/`ROTATE`. Objects and events are extracted; ambiguity is in **forcing one global rule** across demos.

### Branched per-demo hypotheses — designed and implemented

When `len({frozenset(demo_transform_types) for demos}) > 1`, `RuleCandidateGenerator` (current code in `asra-arc/src/asra/perception/rules.py`) emits:

1. **`BRANCHED_PER_DEMO`** — confidence 1.0, `rule_scope=branched` (top-ranked when demos disagree)
2. **`PER_DEMO_{i}_{DOMINANT_TYPES}`** — one rule per demonstration index

This addresses the 17 heterogeneous tasks epistemically: inconsistency becomes explicit structure instead of a low-confidence `PER_OBJECT_*` guess.

---

## What needs qualification

### Stored batch JSON vs current generator

**Important:** The 800 per-task JSON files in the repo (under `reports/`, gitignored but present locally) were produced **before** branched rules were added, or were **not refreshed** after the code change.

Verification on stored reports (June 2026):

```text
training:   top=BRANCHED_PER_DEMO → 0 tasks
            top confidence < 1.0  → 8 tasks
            top confidence = 1.0  → 392 tasks

evaluation: top=BRANCHED_PER_DEMO → 0 tasks
            top confidence < 1.0  → 9 tasks
            top confidence = 1.0  → 391 tasks
```

Example exception `22eb0ac0` still shows top rule `PER_OBJECT_CREATE` (confidence 0.67), not `BRANCHED_PER_DEMO`.

| Statement | Accurate? |
|-----------|-----------|
| “Branched rules implemented in Phase 2 code” | ✅ Yes |
| “~2% of tasks need branching” | ✅ Yes (17/800) |
| “Batch artifacts show `BRANCHED_PER_DEMO` as top rule on those 17” | ❌ Not until batch re-run |

After re-running batch with current code, expect `num_branched_per_demo ≈ 17` (split 8 + 9) in refreshed summaries.

### “98% common rule coverage”

Committed metric `pct_common_rule_coverage` (~98% training, ~97.75% evaluation) means:

> The **top-ranked rule template** had confidence 1.0 under the **old** global-rule ranking (mostly `APPLY_*` or `PER_OBJECT_*` with full demo support).

It does **not** mean:

- 98% ARC solve rate
- 98% agreement with human program induction
- 98% test-output accuracy

It means **heuristic demo-consistency** for a single global transform hypothesis.

---

## What Phase 2 evaluation does *not* measure

| Often implied | Actually measured |
|---------------|-------------------|
| Solving ARC test outputs | No — demo pairs only |
| Ground-truth transform programs | No — greedy object match + event taxonomy |
| Kaggle / ARC-AGI-3 performance | No — Original ARC batch is offline; Kaggle agent is separate |
| RECOLOR / REFLECT fidelity | Partial — often folded into ROTATE/IDENTITY via `shape_hash` |
| Human-level abstraction | No — coverage and consistency of **our** templates |

Phase 2 success criterion (roadmap): **object-centric reports + plausible rule candidates**, not leaderboard score.

---

## Recommended public wording

### Accurate (use as-is)

> We ran the Phase 2 perception stack on all 800 Original ARC training and evaluation tasks. Every task received at least one rule candidate (100% coverage). On approximately 2% of tasks (17/800), cross-demo transform patterns were heterogeneous under our object-level detector; we added branched per-demo rule hypotheses in the generator for those cases.

### Accurate (Kaggle / interactive track)

> The Phase 2 Kaggle agent (`asra-v0.4-phase2`) applies **compact object-scene hints** to ARC-AGI-3 exploration. That deployment is **not** validated by the Original ARC 800-task batch; the batch validates the offline perception library.

### Overstated (avoid unless batch is re-run)

> We evaluated branched per-demo hypotheses on 800 tasks and they appear as top rules in our published batch reports.

> Phase 2 achieves ~98% abstraction accuracy on ARC.

---

## Relationship to other Phase 2 deliverables

| Deliverable | Scope |
|-------------|--------|
| `asra-arc/src/asra/perception/` | Library — objects, transforms, rules |
| `data/analysis/phase2/` | Original ARC batch metrics & exception docs |
| `asra-phase2-object-centric-reasoning.md` | Theory & architecture (this folder) |
| `asra-phase-2-arc-prize-2026.ipynb` | Interactive agent with object hints (ARC-AGI-3) |

The **theory** (object scenes, transform taxonomy, abductive rule induction, branched demos, soft Phase 1 integration) applies to both tracks. The **800-task numbers** apply only to Original ARC batch evaluation.

---

## Refresh batch artifacts (align code with JSON)

From repo root, with ARC cloned per `asra-arc/data/arc/README.md`:

```bash
cd asra-arc
pip install -e '.[dev]'

python scripts/run_phase2_arc_batch.py \
  --arc-root data/arc/original/training \
  --output-dir data/analysis/phase2/reports/training

python scripts/run_phase2_arc_batch.py \
  --arc-root data/arc/original/evaluation \
  --output-dir data/analysis/phase2/reports/evaluation

python scripts/eval_phase2_batch.py \
  --report-dir data/analysis/phase2/reports/training \
  --output data/analysis/phase2/summary_training.json \
  --label training

python scripts/eval_phase2_batch.py \
  --report-dir data/analysis/phase2/reports/evaluation \
  --output data/analysis/phase2/summary_evaluation.json \
  --label evaluation
```

After refresh, check:

- `summary_*.json` → `num_branched_per_demo` / `pct_branched_per_demo`
- Exception tasks → top `pattern` = `BRANCHED_PER_DEMO`
- Update `PHASE2_EVALUATION_REPORT.md` if headline numbers change

---

## Metric glossary

| Metric | Definition |
|--------|------------|
| `num_with_rule_candidates` | Tasks with non-empty `rule_candidates` list |
| `num_common_rule_coverage` | Tasks where `rule_candidates[0].confidence >= 1.0` (ranking depends on generator version) |
| `num_branched_per_demo` | Tasks where `rule_candidates[0].pattern == "BRANCHED_PER_DEMO"` (post-refresh) |
| `exception_task_ids` | Tasks where top rule `confidence < 1.0` under pre-branch summaries |
| `avg_objects_per_input_scene` | Mean object count in input scenes across demo pairs |
| `avg_transform_events_per_pair` | Mean transform events per input→output demo pair |

---

## References

- Full report: `asra-arc/data/analysis/phase2/PHASE2_EVALUATION_REPORT.md`
- Exception analysis: `asra-arc/data/analysis/phase2/EXCEPTIONS_REPORT.md`
- Rule generator: `asra-arc/src/asra/perception/rules.py`
- Eval aggregator: `asra-arc/scripts/eval_phase2_batch.py`
- Concept article: [`asra-phase2-object-centric-reasoning.md`](asra-phase2-object-centric-reasoning.md)
