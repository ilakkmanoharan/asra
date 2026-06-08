# Phase 1 — Implementation Reference

**Agent tag:** `asra-v0.1-phase1`  
**Notebook:** `asra-phase-1-arc-prize-2026.ipynb` (derived from v4-fixed / v11.4 bootstrap)

---

## Kaggle notebook flow

1. Bootstrap `asra_venv` with competition wheels (`--without-pip`, `--target site-packages`, `--no-deps`).
2. Mirror `arc_agi_3_wheels`, `ARC-AGI-3-Agents`, `environment_files` into working bundle.
3. Write embedded `my_agent.py` (`ASRAAgent`, `ActionSemanticsInferencer`, `ASRAExplorer`).
4. Smoke-test: `venv_python my_agent.py --self-test`.
5. Write `submission.parquet` (validation gate).

Scoring re-executes `my_agent.py` → `run_swarm()` → API play. Do not run Swarm in the notebook during validation beyond self-test.

---

## Embedded agent modules

| Class | Role |
|-------|------|
| `ActionSemanticsInferencer` | Effect table per `(state_hash, action)` |
| `ASRAExplorer` | Novelty + uncertainty + reward scoring |
| `ASRAAgent` | Swarm agent: RESET lifecycle, frame diffs, choose_action |

**Reasoning string:** `ASRA v0.3: ACTION3` (embedded tag; submit message uses `asra-v0.1-phase1`).

---

## Library parity (`asra-arc`)

| Kaggle embed | Library module |
|--------------|----------------|
| `state_hash` | `transition_schema.py` |
| `ActionSemanticsInferencer` | `agent/action_tester.py` coarse buckets |
| `ASRAExplorer` | `agent/exploration_policy.py` |
| Dead-end tabu | `agent/dead_end_detector.py` |
| Swarm orchestration | `env/arc_agi3_runner.py` |

---

## CLI (local research)

```bash
cd asra-arc
pip install -e .
python -m asra complete-phase1
python -m asra replay --episode <id>
```

Exports: `data/exports/asra_v0_1_transitions.jsonl`, `data/graphs/state_graph.json`

---

## Regenerate notebook

The Phase 1 notebook is maintained as the canonical v4-fixed artifact. After agent logic changes, update the embedded `MY_AGENT_CODE` cell or add `build_phase1_kaggle_notebook.py` (future).

---

## Submit workaround

`GetKernelSessionStatus` often returns HTTP 500. Pattern:

```bash
./submit.sh push                    # or: python3 push_and_submit.py --push-only
sleep 900                           # wait for Run All
./submit.sh submit 1 "asra-v0.1-phase1"
```
