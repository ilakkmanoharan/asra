# Phase 1 — Experience Engine (End-to-End Specification)

**Timeline:** May → June 2026  
**Agent tag:** `asra-v0.1-phase1`  
**Status:** **COMPLETE** — library + Kaggle parity submit  
**Primary dataset:** ARC-AGI-3 (competition + mock replay)

---

## Primary goal

Deliver the **scientific observation and experimental memory infrastructure** of ASRA:

```text
observe → log τ → infer semantics → explore → export dataset
```

**Success criterion (Phase 1):** reproducible interaction-to-knowledge pipeline — not leaderboard optimization.

---

## Deliverables

| # | Module | Location |
|---|--------|----------|
| 1 | ARC-AGI-3 runner | `asra-arc/src/asra/env/arc_agi3_runner.py` |
| 2 | Episode logger | `memory/episode_logger.py` |
| 3 | State graph | `memory/state_graph.py` → `data/graphs/` |
| 4 | Action semantics (coarse) | Kaggle `ActionSemanticsInferencer` |
| 5 | Exploration policy | `agent/exploration_policy.py` + Kaggle `ASRAExplorer` |
| 6 | Dead-end detector | `agent/dead_end_detector.py` |
| 7 | Transition export | `data/exports/asra_v0_1_transitions.jsonl` |
| 8 | Replay + viewer | CLI `replay`, Streamlit viewer |
| 9 | Kaggle agent | `kaggle-notebooks/phase1/asra-phase-1-arc-prize-2026.ipynb` |

---

## Non-goals

- Object abstraction (Phase 2)
- Exploration graphs / subgoals (Phase 3)
- Causal semantics (Phase 4)
- Goal inference (Phase 5)
- Planning (Phase 6)

---

## Kaggle package

| File | Role |
|------|------|
| `asra-phase-1-arc-prize-2026.ipynb` | Submit notebook (v4-fixed bootstrap) |
| `push_and_submit.py` / `submit.sh` | CLI push + submit |
| `kernel-metadata.json` | Kaggle metadata |

### Submit

```bash
cd kaggle-notebooks/phase1
./submit.sh all "asra-v0.1-phase1"
```

**Kernel:** https://www.kaggle.com/code/ilakkmanoharan/asra-phase-1-arc-prize-2026

---

## Milestone checklist

| ID | Milestone | Status |
|----|-----------|--------|
| **1A** | Transition schema + hash stability | done |
| **1B** | Episode logger + state graph | done |
| **1C** | Exploration + dead-end policy | done |
| **1D** | `complete-phase1` reproducible pipeline | done |
| **1E** | Kaggle `asra-v0.1-phase1` on scoreboard | done (parity) |
| **1F** | SciLayer preprint v3 | done |

---

## Full specification

See `documents/ASRA_Phase1_Official_Technical_Specification.md` for module-level detail, data paths, and CLI reference.

**Conceptual paper:** [`asra-phase1-transition-centric-experience.md`](asra-phase1-transition-centric-experience.md)
