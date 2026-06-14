# ASRA Evaluation Report — ARC-AGI-3 & Phase Benchmarks (v0)

**Author:** Ilakkuvaselvi Manoharan  
**Affiliation:** Nature Foundation Models  
**Date:** May 2026  
**Status:** Interim preprint v0 (SciLayer Systems) — **in progress**  
**Repository copy:** `documents/evaluation/asra-arc-agi-3-evaluation-report-v0.md`  
**SciLayer:** https://sci-layer.vercel.app/articles/asra-arc-agi-3-evaluation-report-v0  
**Target:** v1 after Stage 1 gateway migration completes (Phases 1–9 all **Succeeded**)

> **Purpose:** Consolidated metrics document for ASRA Phases 1–9: competition scores, benchmark results, agent version ladder, and evaluation tracks. **v0** publishes available evidence now; sections marked **TBD** fill as Stage 1 submits complete and Stage 2 score work begins.

---

## Document status (v0)

| Section | Status | Notes |
|---------|--------|-------|
| Executive summary | **Partial** | P1–2 scores only |
| Track A — gateway plumbing | **Complete** | See gateway spec |
| Track B — competition scores | **Partial** | 2/9 phases submitted |
| Track C — repeated-run learning | **Protocol only** | Results TBD |
| Phase 2 Original ARC | **Complete** | See Phase 2 results paper |
| Phases 3–9 benchmarks | **TBD** | Pending Stage 1 + library evals |
| Agent version ladder | **Partial** | v0.1–v0.4 verified |
| Limitations | **Draft** | |

**Upgrade path:** v0 → v1 when Stage 1 exit criteria met ([gateway migration complete](https://sci-layer.vercel.app/articles/arc-agi-3-kaggle-gateway-deployment-spec)).

---

## 1. Executive summary

ASRA implements a nine-layer transition-centric cognitive stack for adaptive reasoning on ARC-AGI-3. This report consolidates **three evaluation tracks**:

| Track | Question | v0 status |
|-------|----------|-----------|
| **A. Plumbing** | Does Kaggle score the notebook? | **Solved** — gateway sidecar pattern |
| **B. Intelligence** | How well does each phase agent play? | **Partial** — P1 **0.03**, P2 **0.00** |
| **C. Learning** | Does the agent improve on repeat? | **Protocol published**; results pending |

**Key v0 findings:**

1. Generic **Kaggle Error** on ARC-AGI-3 was an evaluation-contract mismatch, not platform failure — fixed by official gateway pattern (Phase 1 v3 ref **53652655**).
2. Gateway migration verified on Phase 2 (ref **53660658**, score **0.00**).
3. Phase 2 Observation Engine: **100%** rule-candidate coverage on 800 Original ARC tasks ([results paper](https://sci-layer.vercel.app/articles/asra-phase-2-original-arc-evaluation-results)).
4. Stage 1 in progress: Phases 3–9 gateway submits pending (1 submission/day limit).

---

## 2. Evaluation tracks

### 2.1 Track A — Evaluation plumbing (Kaggle gateway)

**Status:** Complete for Phase 1–2; migration tooling ready for Phases 3–9.

| Requirement | Status |
|-------------|--------|
| Official 4-cell notebook layout | ✅ `_shared/gateway_notebook.py` |
| Template agent (`MyAgent`, no Swarm) | ✅ Phases 1–9 extracted |
| Dummy parquet schema | ✅ `row_id, game_id, end_of_game, score` |
| Scoring rerun via gateway sidecar | ✅ Verified P1, P2 |

**Reference:** [ARC-AGI-3 Kaggle Gateway Deployment Spec](https://sci-layer.vercel.app/articles/arc-agi-3-kaggle-gateway-deployment-spec)

### 2.2 Track B — Competition intelligence (public score)

**Metric:** Kaggle public score after gateway scoring rerun (single run per submit).

**Stage 1 goal:** Green **Succeeded** status per phase — not score optimization.

| Phase | Agent tag | Kernel | Ref | Status | Public score |
|-------|-----------|--------|-----|--------|--------------|
| 1 | `asra-v0.1-phase1` | v3 | **53652655** | Succeeded | **0.03** |
| 2 | `asra-v0.4-phase2` | v5 | **53660658** | Succeeded | **0.00** |
| 3 | `asra-v0.5-phase3` | v2 | — | Push done; submit pending | **TBD** |
| 4 | `asra-v0.6-phase4` | — | — | Not submitted | **TBD** |
| 5 | `asra-v0.7-phase5` | — | — | Not submitted | **TBD** |
| 6 | `asra-v0.8-phase6` | — | — | Not submitted | **TBD** |
| 7 | `asra-v0.85-phase7` | — | — | Not submitted | **TBD** |
| 8 | `asra-v0.9-phase8` | — | — | Not submitted | **TBD** |
| 9 | `asra-v1.0-phase9` | — | — | Not submitted | **TBD** |

**Interpretation (v0):** Phase 1 baseline (transition logging + exploration) achieves non-zero score (**0.03**). Phase 2 adds object-scene hints without score gain on first gateway submit — expected at Stage 1; score iteration is Stage 2+.

**Historical note:** Pre-gateway submits (v1/v2) for all phases returned generic **Kaggle Error** — not comparable scores.

### 2.3 Track C — Repeated-run adaptive learning

**Status:** Protocol published; empirical results **TBD**.

**Protocol:** [Repeated-Run Learning Eval for ARC-AGI-3](https://sci-layer.vercel.app/articles/asra-repeated-run-eval-arc-agi-3)

| Setup | Description | v0 results |
|-------|-------------|------------|
| **A** | Full-game repetition (ls20, bp35) | **TBD** |
| **B** | Single-level repetition | **TBD** |

**Primary metrics (when run):** action count, dead-end revisit rate, visit redundancy, adaptive vs fresh-agent control.

**Constraint:** Kaggle daily submit does not persist memory between competition reruns — Track C measured in research library (`asra-arc`) or instrumented kernels.

---

## 3. Phase-by-phase metrics

### 3.1 Phase 1 — Experience Engine

| Metric | Value | Source |
|--------|-------|--------|
| Transition schema tests | 24 pass | `pytest` |
| Hash stability audit | **PASS** | `complete-phase1` |
| Export pipeline | JSONL + Parquet + CSV | `data/exports/asra_v0_*` |
| Kaggle gateway submit | Succeeded | ref **53652655** |
| Public score | **0.03** | Track B |
| Live ARC-AGI-3 API episode | Pending credentials | — |

**Theory:** [Phase 1 preprint](https://sci-layer.vercel.app/articles/transition-centric-adaptive-reasoning-asra-phase-1)

### 3.2 Phase 2 — Observation Engine

| Metric | Training | Evaluation |
|--------|----------|------------|
| Rule-candidate coverage | 100% (400/400) | 100% (400/400) |
| Common-rule coverage (conf 1.0) | 98.0% | 97.75% |
| Avg objects / scene | 13.16 | 25.40 |
| Avg transform events / pair | 16.86 | 30.90 |
| Parse errors | 0 | 0 |

**Full report:** [Phase 2 Original ARC Evaluation Results](https://sci-layer.vercel.app/articles/asra-phase-2-original-arc-evaluation-results)

| Metric | Value | Source |
|--------|-------|--------|
| Kaggle gateway submit | Succeeded | ref **53660658** |
| Public score | **0.00** | Track B |

### 3.3 Phase 3 — Exploration & Memory

| Metric | v0 status |
|--------|-----------|
| MiniGrid / BabyAI benchmarks | Library complete — **TBD** consolidated table |
| DoorKey benchmark | **TBD** |
| Kaggle gateway submit | Push complete — submit **TBD** |
| Public score | **TBD** |

**Theory:** [Phase 3 preprint](https://sci-layer.vercel.app/articles/directed-exploration-episodic-memory-asra-phase-3)  
**Spec:** [Phase 3 technical specification](https://sci-layer.vercel.app/articles/asra-phase-3-exploration-memory-navigation-spec)

### 3.4 Phase 4 — Causal Action Semantics

| Metric | v0 status |
|--------|-----------|
| Semantic accuracy / calibration | **TBD** |
| Counterfactual query tests | **TBD** |
| Kaggle submit | **TBD** |

### 3.5 Phase 5 — Goal Inference

| Metric | v0 status |
|--------|-----------|
| Hypothesis ranking accuracy | **TBD** |
| Progress detection | **TBD** |
| Kaggle submit | **TBD** |

### 3.6 Phase 6 — Planning & Strategy

| Metric | v0 status |
|--------|-----------|
| Planner success rate | **TBD** |
| Actions-to-win | **TBD** |
| Kaggle submit | **TBD** |

### 3.7 Phase 7 — Robustness & Generalization

| Metric | v0 status |
|--------|-----------|
| Stuck / waste detection | **TBD** |
| Procgen / DMLab delta | **TBD** |
| Eval dashboard | **TBD** — `data/robustness/dashboard/` |
| Kaggle submit | **TBD** |

### 3.8 Phase 8 — Decision Biology Bridge

| Metric | v0 status |
|--------|-----------|
| Pathway hypothesis rank | **TBD** |
| Kaggle submit | **TBD** |

### 3.9 Phase 9 — Integration

| Metric | v0 status |
|--------|-----------|
| Full stack self-test | Local pass — **TBD** Kaggle gateway |
| Integrated hint weights | `ASRA_*_HINT_WEIGHT` env-tunable |
| Kaggle submit (v1.0) | **TBD** |
| Demo video | **TBD** |
| Architecture diagram SVG | **TBD** |

---

## 4. Agent version ladder

Cumulative agent tags embedded in Kaggle template agents:

| Version | Phase | Layers active | Kaggle verified (gateway) | Score |
|---------|-------|---------------|---------------------------|-------|
| v0.1 | 1 | Experience | ✅ ref 53652655 | 0.03 |
| v0.4 | 2 | + Observation | ✅ ref 53660658 | 0.00 |
| v0.5 | 3 | + Memory / exploration | Push only | TBD |
| v0.6 | 4 | + Causality | — | TBD |
| v0.7 | 5 | + Goals | — | TBD |
| v0.8 | 6 | + Planning | — | TBD |
| v0.85 | 7 | + Robustness | — | TBD |
| v0.9 | 8 | + Biology bridge | — | TBD |
| v1.0 | 9 | Full integration | — | TBD |

**v1 report goal:** Complete score column + layer ablation (disable Phase N hints → measure Δ score).

---

## 5. Data sources

| Path | Content |
|------|---------|
| `asra-arc/data/analysis/phase2/` | Original ARC eval (complete) |
| `asra-arc/data/exports/` | Transition datasets |
| `asra-arc/data/robustness/` | Phase 7 dashboard (partial) |
| `kaggle-notebooks/phaseN/` | Per-phase agents + notebooks |
| Kaggle submissions API | Competition refs + scores |

---

## 6. Roadmap to v1

| Step | Action | Unblocks |
|------|--------|----------|
| 1 | Complete Stage 1 submits (P3→P9) | Full Track B score ladder |
| 2 | Stage 2 — iterate Phase 1/9 score | Non-zero competitive scores |
| 3 | Run repeated-run protocol (ls20/bp35) | Track C results |
| 4 | Consolidate Phase 3–7 library benchmarks | Phase sections 3.3–3.7 |
| 5 | Architecture SVG + demo video | Phase 9 narrative |
| 6 | Publish **Evaluation Report v1** | Final Phase 9 deliverable |

---

## 7. Limitations (v0)

1. **Incomplete score ladder** — only Phases 1–2 gateway-verified at time of writing.
2. **Single-run scores** — no repeated-run learning evidence in Track B.
3. **Original ARC ≠ ARC-AGI-3** — Phase 2 benchmark is static perception; competition is interactive.
4. **Daily submit cap** — 1/day slows Stage 1 completion.
5. **Pre-gateway scores invalid** — earlier ERROR submits excluded from comparison.

---

## 8. References

- [ASRA Integrated Architecture](https://sci-layer.vercel.app/articles/asra-integrated-architecture)
- [Gateway Deployment Spec](https://sci-layer.vercel.app/articles/arc-agi-3-kaggle-gateway-deployment-spec)
- [Repeated-Run Eval Protocol](https://sci-layer.vercel.app/articles/asra-repeated-run-eval-arc-agi-3)
- [Phase 2 Original ARC Results](https://sci-layer.vercel.app/articles/asra-phase-2-original-arc-evaluation-results)
- [Phase 1–9 preprints](https://sci-layer.vercel.app/articles)
- ASRA repo: https://github.com/ilakkmanoharan/asra

---

## 9. One-line takeaway (v0)

**ASRA v0 evaluation confirms gateway scoring works (Track A), establishes Phase 2 perception on 800 ARC tasks, and records first competition scores (P1: 0.03, P2: 0.00) — v1 completes the phase ladder once Stage 1 migration finishes.**
