# Phase 4 — Implementation Reference

**Status:** Milestones 4A–4B complete (library + Kaggle agent); 4C PHYRE optional pending  
**Agent tag:** `asra-v0.6-phase4`  
**Library:** `asra-arc/src/asra/causality/`

---

## Modules

| Module | Role |
|--------|------|
| `schemas.py` | `ChangeReport`, `ActionEffectSignature`, `TransitionPrediction`, `CausalHypothesis`, `CounterfactualResult` |
| `change_analyzer.py` | Unified cell + object/transform diff (Phase 1 + Phase 2) |
| `effect_summarizer.py` | Aggregate `(game, state, action)` → semantic label + confidence |
| `transition_model.py` | Lookup-based `P(s′\|s,a)` feature prediction |
| `uncertainty.py` | Epistemic uncertainty per action |
| `hypothesis_tester.py` | Confirm/refute causal hypotheses |
| `counterfactual.py` | Alternate-action simulation (lookup + model) |
| `semantics_store.py` | Online ingest + persistent semantics JSON |
| `arc_semantics.py` | Batch mine JSONL + `eval_prediction_mae` |
| `policy_v3.py` | `CausalExplorationPolicyV3` extends Phase 3 policy v2 |

---

## CLI

```bash
cd asra-arc
PYTHONPATH=src python3 -m asra build-action-semantics \
  --input-dir data/transitions \
  --output-dir data/causality/arc/semantics

PYTHONPATH=src python3 -m asra eval-phase4-arc \
  --input-dir data/transitions \
  --output data/analysis/phase4/arc_semantics_eval.json
```

Scripts (direct):

```bash
PYTHONPATH=src python3 scripts/build_action_semantics.py --input-dir data/transitions
PYTHONPATH=src python3 scripts/eval_phase4_arc_semantics.py
```

---

## Tests

```bash
cd asra-arc && PYTHONPATH=src python3 -m pytest tests/test_causality.py -q
# 67 total tests (Phase 1–4)
```

---

## Kaggle package (`kaggle-notebooks/phase4/`)

| File | Role |
|------|------|
| `asra_phase4_my_agent.py` | Competition agent — embedded `CausalSemanticsEngine` |
| `asra-phase-4-arc-prize-2026.ipynb` | Submit notebook (bootstrap → write agent → self-test → parquet) |
| `kernel-metadata.json` | Kaggle kernel metadata |
| `push_and_submit.py` / `submit.sh` | Push + submit helpers |

**Build notebook from agent:**

```bash
python3 asra-arc/scripts/build_phase4_kaggle_notebook.py
```

**Local self-test (no ARC runtime):**

```bash
python3 kaggle-notebooks/phase4/asra_phase4_my_agent.py --self-test
```

**Submit to Kaggle:**

```bash
cd kaggle-notebooks/phase4
./submit.sh all "ASRA v0.6-phase4 causal semantics"
```

---

## Transition metadata (Phase 4)

When using `SemanticsStore.ingest_transition`, transitions gain:

```json
"metadata": {
  "causality": {
    "effect_signature_id": "...",
    "semantic_label": "translate",
    "confidence": 0.82,
    "uncertainty": 0.15,
    "predicted_changed_cells": 4.2,
    "transform_histogram": {"translate": 2}
  }
}
```

---

## Data paths

```text
asra-arc/data/causality/arc/semantics/   # per-game semantics JSON
asra-arc/data/analysis/phase4/           # eval reports
```

---

## Milestone status

| Milestone | Status |
|-----------|--------|
| **4A** ARC semantics foundation | done — `causality/` package, batch miner, tests |
| **4B** Transition model + uncertainty | done — model, scorer, change analyzer, eval script |
| **4C** Hypotheses + PHYRE | partial — hypothesis + counterfactual done; PHYRE adapter pending |
| **4D** Kaggle v0.6-phase4 | done — agent + notebook + submit helpers |

See [phase4-action-semantics-causal-inference.md](phase4-action-semantics-causal-inference.md) for full spec.
