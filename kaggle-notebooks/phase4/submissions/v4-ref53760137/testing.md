# Testing — Phase 4 v4

## Pre-submit (local)

- [x] `python3 -m py_compile asra_phase4_kaggle_template_agent.py`
- [x] `class CausalSemanticsEngine` present before `GLOBAL_SEMANTICS`
- [x] `from arcengine import FrameData, GameAction, GameState` before `MyAgent`
- [x] Rebuild notebook — cell 2 contains embedded engine

## Validation run

| Check | Result |
|-------|--------|
| Push kernel v4 | OK |
| Run All | **COMPLETE** |
| `submission.parquet` | Present |

## Scoring rerun

| Check | Result |
|-------|--------|
| Status | **Succeeded** (ref 53760137) |
| Public score | **0.00** |

## Regression guard

`extract_template_agent.py` now copies bootstrap-section `class` blocks — run before Phase 5+ extract:

```bash
python3 kaggle-notebooks/_shared/extract_template_agent.py --phase 5 --force
grep -q 'class CausalSemanticsEngine' kaggle-notebooks/phase5/asra_phase5_kaggle_template_agent.py
```
