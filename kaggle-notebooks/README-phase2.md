# ASRA Phase 2 — Kaggle submission

## Notebook

**[asra-phase-2-arc-prize-2026.ipynb](asra-phase-2-arc-prize-2026.ipynb)** — submit this to [ARC Prize 2026 — ARC-AGI-3](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3).

## What it does

1. Bootstraps `asra_venv` and installs competition wheels (same pattern as Phase 1 v4-fixed).
2. Writes **`my_agent.py`** (`asra-v0.4-phase2`) with embedded compact object-scene perception.
3. Smoke-tests `my_agent.py --self-test` inside the venv.
4. Writes **`submission.parquet`** (validation gate).

Scoring re-executes `my_agent.py` — do not run Swarm in the notebook.

## Source files

| File | Role |
|------|------|
| `asra_phase2_my_agent.py` | Agent source of truth |
| `asra_phase2_compact_perception.py` | Standalone perception helpers (mirrored in agent) |
| `../asra-arc/scripts/build_phase2_kaggle_notebook.py` | Regenerate `.ipynb` after editing agent |

```bash
cd asra-arc && python scripts/build_phase2_kaggle_notebook.py
```

## Local smoke test

```bash
python kaggle-notebooks/asra_phase2_my_agent.py --self-test
```

Full Swarm requires competition wheels + `ASRA_COMP_ROOT`.
