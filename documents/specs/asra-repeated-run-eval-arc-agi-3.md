# Repeated-Run Learning Evaluation for ARC-AGI-3 — Protocol and ASRA Mapping

**Author:** Ilakkuvaselvi Manoharan  
**Affiliation:** Nature Foundation Models  
**Date:** May 2026  
**Status:** Published preprint (SciLayer Systems)  
**Repository copy:** `documents/specs/asra-repeated-run-eval-arc-agi-3.md`  
**SciLayer:** https://sci-layer.vercel.app/articles/asra-repeated-run-eval-arc-agi-3  
**Companion:** [ASRA Phase 1](https://sci-layer.vercel.app/articles/transition-centric-adaptive-reasoning-asra-phase-1), [Phase 3](https://sci-layer.vercel.app/articles/directed-exploration-episodic-memory-asra-phase-3)

> **Purpose:** Formalize an evaluation protocol for measuring **genuine learning across repeated ARC-AGI-3 episodes** — not single-episode peak score alone. Defines setups, metrics, persistence requirements, and how ASRA's transition-centric stack produces measurable run-over-run improvement.

---

## 1. Motivation

ARC-AGI-3 is an **interactive** benchmark: agents act, observe state changes, and accumulate evidence over many steps. A single competition score answers:

> *Did this agent solve anything on this run?*

It does **not** answer:

> *Does the agent learn from prior interaction — fewer actions, fewer dead ends, better semantics — when the same game or level is attempted again?*

Repeated-run evaluation separates **memorization of a fixed policy** from **adaptive reasoning**: updating action semantics, visit memory, and plans from transition evidence collected on earlier attempts.

This protocol draws on community discussion of full-game vs single-level repetition (including games **ls20** and **bp35** as practical test beds) and aligns with ASRA's core loop: log transitions → infer semantics → avoid dead ends → explore efficiently on the next attempt.

---

## 2. Evaluation question

**Primary hypothesis (adaptive agent):**

> Repeated interaction with the same game or level should monotonically improve efficiency metrics — holding environment stochasticity and agent seed policy fixed — if learning is occurring.

**Null hypothesis (fresh agent each run):**

> Run *k* and run *k*+1 are independent; action count and error rate do not decrease unless by chance.

Distinguishing these requires **explicit persistence** of memory artifacts between runs and **paired comparison** of trajectories.

---

## 3. Setup A — full-game repetition

**Procedure:**

1. **Run 1:** Agent plays the full game from initial state to terminal (win, loss, or max actions). Log full transition sequence τ₁.
2. **Run 2:** Agent replays the **same game** with memory from Run 1 loaded. Log τ₂.
3. **Run 3+:** Continue until action count plateaus or max runs *R* reached.

**Compare:** τ₁ vs τ₂ vs τ₃ — action sequences, visit maps, dead-end revisits, time-to-win.

**Success criterion (Setup A):**

```text
actions(run_k) < actions(run_{k-1})   for some k ≥ 2
AND
dead_end_revisits(run_k) < dead_end_revisits(run_{k-1})
```

**Interpretation:** If Run 3 beats Run 2 on action count **and** reduces repeated dead-end `(state, action)` pairs, the agent is using cross-run memory — not just lucky exploration noise.

---

## 4. Setup B — single-level repetition

**Procedure:**

1. Fix a **single level** within a game (e.g. one stage of ls20 or bp35).
2. **Run 1:** Play level from entry state to level terminal or cap.
3. **Run 2+:** Replay the **same level** with persisted memory.

**Compare:** Per-level action count, unique states visited, subgoal completion time.

**Success criterion (Setup B):**

```text
median_actions_per_level(run_k) decreases across k
AND
visit_redundancy(run_k) decreases  (fewer re-visits to same state_hash)
```

Setup B isolates learning at finer granularity — useful when full-game variance dominates.

---

## 5. Primary metrics

| Metric | Definition | Learning signal |
|--------|------------|-----------------|
| **Action count** | Total `GameAction` steps to terminal | Lower on later runs → efficiency gain |
| **Dead-end revisit rate** | Fraction of steps repeating a taboo `(state_hash, action)` | Lower → semantics / dead-end memory working |
| **Visit redundancy** | `revisits / unique_states` per episode | Lower → exploration memory working |
| **Time-to-first-progress** | Steps until reward proxy increases | Lower → goal/progress detection improving |
| **Semantic confidence** | Mean confidence of inferred action labels on repeated `(s,a)` pairs | Higher → causality layer converging |
| **Trajectory edit distance** | Levenshtein distance between action sequences run *k* vs *k*−1 | Decreasing divergence with lower action count → stable improvement, not random |

**Secondary metrics (competition-aligned):**

| Metric | Source |
|--------|--------|
| Public Kaggle score | `submission.parquet` after gateway scoring |
| Levels completed | Episode summary |
| Win rate | Terminal status across runs |

**Important:** Kaggle public score is a **single-run aggregate**. Repeated-run metrics must be collected in **local or instrumented episodes** (research library) or via custom logging inside the competition agent — the default daily submit does not expose run-over-run series.

---

## 6. Cross-run persistence contract

For repeated-run eval to be meaningful, specify what persists between runs:

| Artifact | Persists? | Producer (ASRA) | Purpose |
|----------|-----------|-----------------|---------|
| Transition log JSONL | **Yes** | Phase 1 `EpisodeLogger` | Replay, compare τ₁…τₙ |
| `(state_hash, action) → semantics` map | **Yes** | Phase 1 inferencer, Phase 4 store | Avoid re-discovering action effects |
| Dead-end taboo set | **Yes** | Phase 1 `DeadEndDetector` | Skip known bad actions |
| Visit counts / exploration graph | **Yes** | Phase 3 `VisitationMemory`, `ExplorationGraph` | Reduce redundant exploration |
| Goal hypotheses | **Optional** | Phase 5 | Faster goal lock-in on repeat |
| Plan cache | **Optional** | Phase 6 | Reuse successful action sequences |
| Raw grid frames | **No** (derive from hash) | — | Storage efficiency |

**Fresh-agent control:** Run the same protocol with persistence **disabled** between runs. Adaptive agents should beat fresh-agent controls on action count by run 2–3; if not, claimed "learning" is likely within-run exploration only.

**Kaggle constraint:** Competition reruns typically start a **new scoring episode** without filesystem persistence between daily submits. Repeated-run eval is therefore primarily a **research-library** or **custom instrumented kernel** measurement — not inferable from one public score per day.

---

## 7. ASRA layer mapping

How each ASRA layer contributes to measurable run-over-run improvement:

| Run | Phase | Expected contribution |
|-----|-------|----------------------|
| **Run 1** | Phase 1 | Collect τ = (s, a, s′, r); build state graph; infer preliminary semantics; mark dead ends |
| **Run 2** | Phase 1 + 3 | Taboo dead ends; bias away from high-visit states; replay buffer informs exploration prior |
| **Run 2** | Phase 4 | Higher semantics confidence on seen (s, a); lower uncertainty bonus → less random probing |
| **Run 3** | Phase 5–6 | Goal hypotheses rank faster; plan reuse from strategy library |
| **Run 3+** | Phase 7 | Stuck/waste detectors penalize loops that survived earlier runs |

**Canonical transition (join key across layers):**

```text
τ = (s, a, s′, r, terminal, diff, metadata)
state_hash = SHA-256(canonical grid JSON)
```

All cross-run comparisons should key on `state_hash` and `episode_id` scope — not raw pixel buffers.

---

## 8. Recommended experimental protocol

### 8.1 Games and levels

Start with games suitable for short iteration cycles:

| Target | Setup | Rationale |
|--------|-------|-----------|
| **ls20** | Setup A or B | Community-suggested test bed for repeated-run comparison |
| **bp35** | Setup A or B | Same |
| Additional ARC-AGI-3 games | Setup A | Generalization of learning signal |

Document game ID, level ID, max actions cap, and random seed policy for each run.

### 8.2 Run matrix

Minimum experiment for publication-quality evidence:

| Condition | Persistence | Runs |
|-----------|-------------|------|
| **Adaptive** | Full Phase 1–3 memory | *R* = 5 |
| **Fresh control** | None between runs | *R* = 5 |
| **Random baseline** | N/A | 1 per run slot |

Report mean ± std of action count per run index *k*.

### 8.3 Analysis

1. Plot `actions(k)` and `dead_end_revisits(k)` for adaptive vs fresh.
2. Align trajectories on `state_hash` sequence; compute edit distance between consecutive runs.
3. Export transitions to JSONL; verify hash stability (audit PASS).
4. Optional: ablate Phase 3 memory off — if run-over-run gain disappears, memory layer is causal.

---

## 9. Relation to competition scoring

Two tracks (do not conflate):

| Track | Question | Where measured |
|-------|----------|----------------|
| **A. Evaluation plumbing** | Does Kaggle score the notebook? | Gateway sidecar submit — see [Gateway Deployment Spec](https://sci-layer.vercel.app/articles/arc-agi-3-kaggle-gateway-deployment-spec) |
| **B. Agent intelligence** | How well does the agent play? | Public score (single run) |
| **C. Adaptive learning** | Does the agent improve on repeat? | **This protocol** — local / instrumented runs |

Track C requires persistence and paired runs — outside default Kaggle daily submit semantics.

**Practical recommendation:** Use Track A+B for leaderboard presence; use Track C for research claims about adaptive reasoning.

---

## 10. Submission frequency (eval infrastructure note)

Measuring learning curves meaningfully benefits from **multiple evaluations per day** (e.g. 5–10 submits) to iterate persistence and memory policies quickly. A single daily submit constrains feedback to one scalar — insufficient for run-over-run analysis on the platform itself.

Local replay evaluation (`python -m asra complete-phase1`, transition export, replay viewer) remains the primary loop for Track C regardless of submit quota.

---

## 11. Reporting template

Minimum tables for a repeated-run results section:

**Table 1 — Run-over-run action count (Setup A, game ls20)**

| Run *k* | Actions | Dead-end revisits | Unique states | Win |
|---------|---------|-------------------|---------------|-----|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

**Table 2 — Adaptive vs fresh (Run 3)**

| Condition | Actions (mean ± std) | Δ vs Run 1 |
|-----------|----------------------|------------|
| Adaptive | | |
| Fresh control | | |

**Figure 1:** `actions(k)` line plot, adaptive vs fresh, *R* runs.

---

## 12. Limitations

- **Stochastic environments:** If level layout varies between runs, action count may not decrease monotonically — report distribution, not single pairs.
- **Kaggle isolation:** Default competition rerun does not persist agent memory between daily submits; Track C is research-library first.
- **Score vs efficiency:** Public score may not correlate with action efficiency on repeated runs — report both.
- **Overfitting to one game:** Gains on ls20/bp35 must be replicated on held-out games.

---

## 13. References

- [ASRA Phase 1 — Transition-Centric Experience](https://sci-layer.vercel.app/articles/transition-centric-adaptive-reasoning-asra-phase-1)
- [ASRA Phase 3 — Exploration & Memory](https://sci-layer.vercel.app/articles/directed-exploration-episodic-memory-asra-phase-3)
- [ASRA Phase 3 Technical Specification](https://sci-layer.vercel.app/articles/asra-phase-3-exploration-memory-navigation-spec)
- [ASRA Integrated Architecture](https://sci-layer.vercel.app/articles/asra-integrated-architecture)
- [ARC-AGI-3 Kaggle Gateway Deployment Spec](https://sci-layer.vercel.app/articles/arc-agi-3-kaggle-gateway-deployment-spec)
- [Transition schema (GitHub)](https://github.com/ilakkmanoharan/asra/blob/main/asra-arc/src/asra/memory/transition_schema.py)

---

## 14. One-line takeaway

**A single ARC-AGI-3 score measures one run; repeated-run eval measures whether the agent learns.** Formalize Setup A (full game) or Setup B (single level), persist transition-derived memory between runs, and report action count and dead-end revisits — adaptive agents should beat fresh-agent controls by run 2–3 if reasoning is real.
