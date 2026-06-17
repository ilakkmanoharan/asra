# Theory — Phase 1 Experience Engine (v3)

**Agent tag:** `asra-v0.1-phase1`  
**SciLayer:** https://sci-layer.vercel.app/articles/transition-centric-adaptive-reasoning-asra-phase-1  
**Full paper:** [`theory-source.md`](theory-source.md)

## What this notebook implements

Phase 1 is the **minimal gateway-valid ASRA agent** for ARC-AGI-3:

- Log transitions: `state → action → next_state → reward`
- Hash-stable `state_hash` (SHA-256 over grid JSON)
- Cell-level diff statistics
- **ActionSemanticsInferencer** — coarse semantics from effect patterns (no predefined action labels)
- **ASRAExplorer** — visit-count exploration + dead-end taboo
- No object scenes, no memory graph, no planning

## Gateway notebook structure

1. Install competition wheels (`arc-agi`, `python-dotenv`)
2. `%%writefile /tmp/my_agent.py` — template agent
3. Rerun branch: gateway sidecar → `main.py --agent myagent`
4. Validation gate: dummy `submission.parquet` (`row_id, game_id, end_of_game, score`)

## Design intent for this submit

**Track A:** Prove official Kaggle evaluation path works after 20+ generic errors.  
**Track B:** Establish baseline public score for Experience-only agent.

## Murphy × ASRA

Pure **ASRA Phase 1** — transition logging and empirical semantics. No BLF/AutoHarness/CWM yet.
