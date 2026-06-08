# Transition-Centric Experience: ASRA Phase 1 — From Unknown Actions to Empirical Reasoning

**Author:** Ilakkuvaselvi (Ilak) Manoharan  
**Affiliation:** Nature Foundation Models  
**Date:** June 2026  
**Version:** 1.0 — conceptual article for the Phase 1 Experience Engine track (companion to `asra-phase-1-arc-prize-2026.ipynb`)

---

## Abstract

Adaptive intelligence in unfamiliar environments cannot begin with predefined policies. The environment does not publish action manuals, win conditions, or transition rules. **ASRA Phase 1** establishes the **Experience Engine** — a minimal agent architecture that treats every intervention as an experiment: observe grid state, apply an action token, measure cell-level diffs and reward proxies, accumulate transition evidence, infer coarse action semantics conditioned on state identity, and explore under uncertainty while tabooing empirically dead ends.

We describe Phase 1 as the **foundation layer** of the Adaptive Scientific Reasoning Architecture: transition logging (`τ = (s, a, s′, r)`), hash-stable state IDs, effect-based semantics inference, information-directed exploration, Swarm-scale multi-game orchestration, and competition-grade execution fidelity (isolated venv, validation vs. scoring separation). The research library lives in `asra-arc/` (`env/`, `memory/`, `agent/`); the Kaggle agent embeds a compact `ASRAAgent` with `ActionSemanticsInferencer` and `ASRAExplorer`.

This article presents the full theory and architecture. Phase 1 does not solve ARC optimally — it builds the **reproducible interaction-to-knowledge pipeline** every later phase depends on.

---

## 1. The architectural foundation Phase 1 establishes

```text
Phase 1   Experience Engine     — transitions, hashes, semantics, exploration
Phase 2   Observation Engine    — objects, transforms, rule hypotheses
Phase 3   Navigation & Memory   — graphs, novelty, subgoals
Phase 4   Causality             — intervention semantics, prediction
Phase 5+  Goals, planning, robustness, biology, integration
```

Phase 1 answers the first scientific question:

> **What happened when we acted, and how can we use that evidence to choose the next intervention?**

Without Phase 1, later phases have nothing to abstract over. Object detectors need consecutive frames; causal models need logged effects; planners need edge tables. Phase 1 is therefore not a placeholder baseline — it is the **empirical substrate** of the entire ASRA program.

```mermaid
flowchart LR
  subgraph P1["Phase 1 — Experience"]
    O[Observe grid]
    L[Log transition τ]
    I[Infer φ̂(a|s)]
    E[Explore]
  end
  subgraph Later["Phases 2–9"]
    Obs[Structure]
    Mem[Memory]
    Cau[Causality]
    Plan[Planning]
  end
  O --> L --> I --> E
  L --> Obs
  L --> Mem
  I --> Cau
  L --> Plan
```

---

## 2. Theoretical stance: experimentation precedes reasoning

Traditional agents assume fixed action semantics: `MOVE_LEFT` means move left because a programmer defined the mapping. ASRA targets **adaptive scientific** settings — novel games, instruments, biological perturbations — where the system receives **tokens without definitions**.

Phase 1 operationalizes one commitment:

```text
Meaning is induced from consequences, not from labels.
```

The primary unit of intelligence is the **transition**:

```text
τ = (s, a, s′, r, terminal, metadata)
```

Memory is not an action transcript; it is growing **transition evidence** linking states, interventions, and measurable diffs. Reasoning is hypothesis formation over latent operators:

```text
φ̂(a | s)  ≈  distribution of Δ(grid) and reward proxy  given (s, a)
```

This framing aligns with ARC-AGI-3 (interactive grid worlds, latent action semantics, sparse feedback) and with **Decision Biology** (perturbations as interventions, expression readouts as state observations). Phase 1 stays game-bound in implementation but establishes the loop both domains share.

| Paradigm | Phase 1 stance |
|----------|----------------|
| Memorize solutions | Rejected — no task-specific cache |
| Random exploration | Rejected — uncertainty-directed probing |
| Symbolic rules upfront | Deferred to Phase 2+ |
| Transition logging first | **Adopted** |
| Reproducible pipelines | **Adopted** — hash-stable exports |

---

## 3. State representation

### 3.1 Canonical grids

Observations are integer grids. ASRA normalizes to canonical 2D integer lists:

```python
def canonical_grid(grid):
    return np.array(grid, dtype=int).tolist()
```

### 3.2 State hashing

Full grids are not stored in inference tables. Each state receives `state_hash = SHA256(JSON(canonical_grid))`. Semantics are keyed by `(state_hash, action)` — the same action may behave differently in different contexts.

Hashing induces an equivalence relation: *s₁ ~ s₂ iff hash(s₁) = hash(s₂)*. The agent reasons over equivalence classes — analogous to **observation buckets** in partially observable control, with the caveat that distinct states may merge.

Phase 2 later adds structural representations (objects, components); Phase 1 accepts hash identity as sufficient for exploratory policy.

---

## 4. Action semantics inference

**ActionSemanticsInferencer** maintains an empirical model per `(state_hash, action)`:

| Recorded | Role |
|----------|------|
| `num_changed_cells` | Effect magnitude from cell diff |
| `reward` | Progress proxy (`levels_completed` when available) |

Inference produces human-readable hypothesis labels:

| Signal | Label |
|--------|-------|
| mean diff = 0 | `no-op / blocked` |
| mean diff ≤ 1.5 | `localized cell update` |
| higher mean | `multi-cell transform` |
| `consistency_score = 1/(1+std)` | reproducibility of effect |

**Epistemic uncertainty:**

```text
u(s,a) = 1                    if no observations
u(s,a) = 1 - min(1, c(s,a))   otherwise
```

High *u* means the agent has not stabilized φ̂(a|s). Phase 1 does not separate aleatoric vs. epistemic variance — both inflate the effect table.

---

## 5. Uncertainty-aware exploration

**ASRAExplorer** scores candidate actions:

```text
score(a) = 2.0 / (1 + n(s,a))     # novelty
         + 0.7 * u(s,a)            # epistemic uncertainty
         + 0.5 * mean_reward(a)    # weak exploitation
         + ε,  ε ~ U(0, 0.05)      # tie-break
```

**Dead-end tabu:** if `(s,a)` produced zero cell changes and non-positive reward, exclude from future consideration at *s*.

**Action space:** simple actions (`ACTION1`–`ACTION5`, `ACTION7`). Complex coordinate actions (`ACTION6`) use center-grid defaults — a placeholder, not a learned pointer.

This is **information-directed probing**: prefer interventions that reduce uncertainty about latent semantics, not random walk.

---

## 6. Agent integration and game lifecycle

**ASRAAgent** implements the closed loop:

| Method | Behavior |
|--------|----------|
| `is_done` | Stop on `WIN` or `MAX_ACTIONS` (default 80) |
| `choose_action` | `RESET` when `NOT_PLAYED` / `GAME_OVER`; else explorer |
| `take_action` | Record action name for attribution |
| `append_frame` | Compute diff; update inferencer and explorer |

| Game state | Agent obligation |
|------------|------------------|
| `NOT_PLAYED` | Issue `RESET` |
| `GAME_OVER` | Issue `RESET` |
| Active play | Choose among **available** simple actions |
| `WIN` | Terminate (`is_done`) |

---

## 7. Swarm orchestration and scorecard aggregation

For competition-scale evaluation, Phase 1 uses official **Swarm** orchestration:

```text
Arcade.get_environments() → [game_id₁, …, game_idₙ]
        ↓
Per game: ASRAAgent instance → scorecard rows
        ↓
submission.parquet (game_id, score, levels_completed, actions, completed)
```

**Design choice:** Phase 1 shares `GLOBAL_SEMANTICS` and `GLOBAL_EXPLORER` across games — treating effect statistics as domain-general. Phase 2+ may isolate per `game_id` to reduce cross-game contamination.

---

## 8. Validation vs. scoring (two-phase evaluation)

Code competitions separate **validation** from **scoring**:

| Phase | What runs | What it proves |
|-------|-----------|----------------|
| **Validation (Run All)** | Bootstrap → write `my_agent.py` → self-test → `submission.parquet` | Artifacts exist; imports succeed |
| **Scoring (re-run)** | Platform executes `my_agent.py` → `run_swarm()` → API play | End-to-end intervention on private games |

Validation success does **not** imply scoring success. Phase 1 research should report both bootstrap pass rate and scorecard aggregates.

---

## 9. Execution fidelity and runtime isolation

The v4-fixed reference pipeline adds **epistemic isolation**:

| Mechanism | Purpose |
|-----------|---------|
| Dedicated `asra_venv` | Competition wheels isolated from host kernel |
| `--system-site-packages` | Host pandas/pyarrow for parquet |
| `pip install --target venv --no-deps` | No host numpy upgrades |
| `os.execve(venv_python)` on agent entry | Scoring uses same interpreter as self-test |
| Stub `agents` package | Load only `tracing`, `recorder`, `agent`, `swarm` |

**Self-test** (`venv_python my_agent.py --self-test`) verifies **process isomorphism** — same interpreter that scores can import runtime — without full API play during validation.

Environment flags: `ASRA_VENV_ACTIVE`, `PYTHONNOUSERSITE=1`, `OPERATION_MODE=COMPETITION`.

---

## 10. Experience Engine library (`asra-arc`)

Phase 1 research code beyond the Kaggle embed:

```text
env/arc_agi3_runner.py      — episode runner
memory/episode_logger.py    — JSONL transitions
memory/state_graph.py       — observed transition graph
agent/exploration_policy.py — simple exploration
agent/dead_end_detector.py  — futile (s,a) detection
transition_schema.py        — hash-stable schema + validation
complete-phase1             — reproducible pipeline CLI
```

**Primary dataset output:** `data/exports/asra_v0_1_transitions.jsonl` — self-generated transition corpus for Phases 2–4.

**Non-goals (Phase 1):** optimal ARC solving, object abstraction, planning, world models, long-horizon strategy.

---

## 11. Agent integration

| Version | Tag | Layer |
|---------|-----|-------|
| Early baselines | `asra-v0.3`, v11.x | Iterative competition fixes |
| **Phase 1 (parity)** | **`asra-v0.1-phase1`** | **Experience Engine — canonical kernel** |

**Kaggle package:** `kaggle-notebooks/phase1/`

```bash
cd kaggle-notebooks/phase1
./submit.sh all "asra-v0.1-phase1"
```

Kernel: `ilakkmanoharan/asra-phase-1-arc-prize-2026`

---

## 12. Position in the ASRA research program

| Question | Phase 1 answer |
|----------|----------------|
| What is memory? | Transition evidence τ |
| What is an action? | Latent token; semantics from effects |
| What is exploration? | Reduce φ̂ uncertainty + avoid dead ends |
| What is success (Phase 1)? | Reproducible pipeline + scorecard participation |
| Bridge to biology | Perturbation → readout = action → state diff |

Phase 1 is the **stress test substrate** for ARC Prize 2026 and the **schema foundation** for Decision Biology transitions in Phase 8.

---

## 13. Open problems

1. **Per-game memory isolation** — reduce cross-game semantics bleed.  
2. **Complex action policies** — learned pointers for `ACTION6`.  
3. **Neural state encoders** — when hash buckets saturate.  
4. **Live ARC-AGI-3 API** — credentials for non-sandbox episodes.  
5. **Phase 2 object scenes** — structural layer atop τ logs.

---

## 14. Conclusion

ASRA Phase 1 proves that adaptive reasoning can begin with **nothing but transitions**: log what changed, infer what actions tend to do in each state, explore where uncertainty is high, and taboo what empirically fails. No objects, no goals, no plans — yet the loop is already scientific: observe, intervene, compare, update beliefs.

The Phase 1 Kaggle agent (`asra-v0.1-phase1`) packages this loop for competition judges. The `asra-arc` library packages it for reproducible research. Every later phase is a refinement of the same question Phase 1 asked first: **what happened when we acted, and what should we try next?**

---

## References (conceptual)

- ASRA Phase 1 specification — `documents/ASRA_Phase1_Official_Technical_Specification.md`  
- Phase 1 implementation — [`phase1-implementation.md`](phase1-implementation.md)  
- Experience Engine CLI — `python -m asra complete-phase1`  
- ARC Prize 2026 — ARC-AGI-3 competition context  
- Decision Biology — perturbation–response analogy (Phase 8 extension)
