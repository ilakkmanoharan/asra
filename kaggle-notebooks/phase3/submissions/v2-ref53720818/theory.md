# Theory — Phase 3 Exploration & Memory (v2)

**Agent tag:** `asra-v0.5-phase3`  
**SciLayer:** https://sci-layer.vercel.app/articles/directed-exploration-episodic-memory-asra-phase-3  
**Full paper:** [`theory-source.md`](theory-source.md)

## What this notebook implements

Phase 3 = Phase 1 + Phase 2 **plus** **CompactExplorationHints**:

| Component | Role |
|-----------|------|
| Visit counts | Per `state_hash` |
| Edge stats | Novelty + usefulness per `(state_hash, action)` |
| Frontier bonus | Prefer less-visited states |
| Repeat penalty | Reduce loops in recent window |
| `exploration_metadata()` | Debug / reasoning strings |

## Cumulative stack

```text
P1: Experience (transitions, semantics, dead-ends)
P2: Observation (object scenes, object_delta)
P3: Memory & exploration (visit/novelty/usefulness)
```

## Design intent for this submit (2026-06-15)

**Track A:** Gateway Succeeded on third kernel (submit-only after prior-day push).  
**Track B:** Informational — does exploration memory change public score?

## Murphy × ASRA

Closest Murphy analogue at this layer: **BLF-like** visit/evidence accumulation (not full probabilistic belief state — that arrives in Phase 4–5).
