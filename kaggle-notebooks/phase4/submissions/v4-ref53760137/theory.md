# Theory — Phase 4 Causal Semantics (v4 ref 53760137)

**Agent tag:** `asra-v0.6-phase4`  
**SciLayer:** https://sci-layer.vercel.app/articles/causal-action-semantics-asra-phase-4  
**Full paper:** [`theory-source.md`](theory-source.md)

## Stack (cumulative)

P1 Experience + P2 Observation + P3 Memory + **P4 CausalSemanticsEngine**:

- Semantic labels from `(state_hash, action)` history
- Transition prediction + confidence + uncertainty
- Counterfactual-style scoring bonuses

## v4 vs v3

v3 failed: `CausalSemanticsEngine` class missing from template → `NameError` at scoring.  
v4 fix: embedded engine + import layout aligned with Phase 3 gateway template.

## Murphy × ASRA

BLF / Code WM analogue — belief over action effects and predicted next states.
