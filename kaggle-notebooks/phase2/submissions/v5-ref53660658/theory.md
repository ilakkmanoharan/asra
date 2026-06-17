# Theory — Phase 2 Observation Engine (v5)

**Agent tag:** `asra-v0.4-phase2`  
**SciLayer:** https://sci-layer.vercel.app/articles/object-centric-adaptive-reasoning-asra-phase-2  
**Full paper:** [`theory-source.md`](theory-source.md)

## What this notebook implements

Phase 2 = Phase 1 **plus** compact **Observation Engine**:

| Component | Role |
|-----------|------|
| Connected components | Segment grid into objects |
| `compact_scene()` | Object count, bboxes, centroids |
| `object_delta()` | Create/destroy/move between frames |
| Object-scene hints | Bias action scoring when cell diffs are ambiguous |

Still embedded in single `MyAgent` — no external `asra-arc` import on Kaggle.

## Cumulative stack

```text
Phase 1: transitions + semantics inferencer + explorer
Phase 2: + object_scene / object_delta hints
```

## Design intent for this submit (2026-06-14)

**Track A:** Verify gateway pattern on second kernel.  
**Track B:** Informational — does object structure help competition score?

## Murphy × ASRA

Structural abstraction layer — prerequisite for later **Code World Models**-style planning (Phase 6), not yet active.
