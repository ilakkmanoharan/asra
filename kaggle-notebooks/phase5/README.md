# Phase 5 — Goal Inference and Hypothesis Engine

**Submissions:** [`submissions/`](submissions/) — *none yet* (archive after first submit).

**Timeline:** August 2026  
**Status:** **SPEC COMPLETE** — Kaggle agent + notebook in this folder; library `goals/` planned in `asra-arc/`  
**Agent tag:** `asra-v0.7-phase5`  
**Depends on:** Phase 1 ✅, Phase 2 ✅, Phase 3 ✅, Phase 4 ✅

---

## Documents

| Document | Role |
|----------|------|
| **[phase5-goal-inference-hypothesis-engine.md](phase5-goal-inference-hypothesis-engine.md)** | Full end-to-end specification |
| **[phase5-implementation.md](phase5-implementation.md)** | Implementation reference (Kaggle + planned library) |
| **[asra-phase5-goal-inference-hypothesis-engine.md](asra-phase5-goal-inference-hypothesis-engine.md)** | **Conceptual paper** (Phase 5 theory) |

**Roadmap sources:** `private/documents/ASRA-theory/ASRA-roadmap-datasets.md`, `ASRA-detailed-roadmap.md`

---

## What Phase 5 adds

Phase 4 learns **what actions do**. Phase 5 learns **what success requires**:

| Module | Capability |
|--------|------------|
| Goal hypothesis generator | Template win conditions (move, match, collect, unlock, avoid, transform) |
| Progress detector | Reward, level change, object/pattern progress signals |
| Object role classifier | agent, target, token, hazard, key, door |
| Hypothesis ranker | Support/refute/score competing goals |
| Experiment planner | Discriminate top-2 hypotheses using Phase 4 uncertainty |

Reasoning string example:

```text
ASRA Phase5: ACTION3 | objects=5 | visits=2 | sem=translate conf=0.81 u=0.12 | goal=move_to_target
```

---

## Kaggle submission

| File | Role |
|------|------|
| `asra-phase-5-arc-prize-2026.ipynb` | Submit notebook |
| `asra_phase5_my_agent.py` | Source agent (embedded in notebook as `my_agent.py`) |
| `build_phase5_kaggle_notebook.py` | Regenerate notebook after agent edits |
| `kernel-metadata.json` | Kaggle metadata |
| `setup_kaggle_cli.sh` | One-time Kaggle CLI setup |
| `submit.sh` / `push_and_submit.py` | Push + submit |

### Build & test

```bash
cd private/phase5
python3 build_phase5_kaggle_notebook.py
python3 asra_phase5_my_agent.py --self-test
```

### Submit

```bash
cd private/phase5
./submit.sh all "ASRA v0.7-phase5 goal inference"
```

---

## Datasets (Phase 5)

| Dataset | Role |
|---------|------|
| ARC-AGI-3 | Primary — hidden goals, progress from play |
| Original ARC | Bootstrap — fully observed goal states |
| PHYRE | Physical success templates |
| CLEVR / CLEVRER | Object roles, relational + temporal goals |

---

## Next engineering step

Implement `asra-arc/src/asra/goals/` per spec §4.5–§6, CLI `build-goal-hypotheses` / `eval-phase5-arc`, and `tests/test_goals.py`.

See [phase5-implementation.md](phase5-implementation.md) for module list and milestone checklist.
