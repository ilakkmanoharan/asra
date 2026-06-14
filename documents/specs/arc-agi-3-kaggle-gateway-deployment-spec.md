# ARC-AGI-3 Kaggle Gateway Deployment Specification

**Author:** Ilakkuvaselvi Manoharan  
**Affiliation:** Nature Foundation Models  
**Date:** May 2026  
**Status:** Published preprint (SciLayer Systems)  
**Repository copy:** `documents/specs/arc-agi-3-kaggle-gateway-deployment-spec.md`  
**SciLayer:** https://sci-layer.vercel.app/articles/arc-agi-3-kaggle-gateway-deployment-spec  
**Companion:** [ASRA Integrated Architecture](https://sci-layer.vercel.app/articles/asra-integrated-architecture)

> **Purpose:** Define the evaluation contract for [ARC Prize 2026 — ARC-AGI-3](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3) on Kaggle so notebooks pass validation **and** private scoring rerun. This spec is derived from the [official ARC-AGI-3 Kaggle Starter](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter) and ASRA's gateway migration (Phase 1 v3, ref **53652655**, public score **0.03**).

---

## 1. Problem statement

Many ARC-AGI-3 submissions fail with a generic message:

> **Kaggle Error:** A system error. Please try resubmitting to resolve the error and contact Kaggle Support if it persists.

**Misleading symptom:** Save & Run All succeeds, `submission.parquet` appears in notebook outputs, and the Kaggle API returns a submission reference. Failure occurs only on the **private scoring rerun** — a second execution Kaggle triggers after Submit.

**Root cause:** The notebook implemented the wrong evaluation contract — typically a standalone agent that calls `run_swarm()` against the public ARC API, instead of registering with the **gateway sidecar** and running `main.py --agent myagent`.

This is an **evaluation plumbing** problem, independent of agent intelligence. A perfect agent will still ERROR if the gateway path is skipped.

---

## 2. Two execution modes

Kaggle ARC-AGI-3 notebooks must branch on `KAGGLE_IS_COMPETITION_RERUN`:

| Mode | Trigger | What runs | Who writes `submission.parquet` |
|------|---------|-----------|----------------------------------|
| **Validation** | env var **unset** (Save & Run All, submit gate) | Install wheels, write agent to `/tmp`, write **dummy** parquet | Notebook (placeholder row) |
| **Scoring rerun** | `KAGGLE_IS_COMPETITION_RERUN=1` (hidden, after Submit) | Wait for gateway → copy framework → register agent → `python main.py --agent myagent` | **Gateway sidecar** records actions and emits real parquet |

```text
Submit click
    │
    ├─► Validation run (user-visible)
    │       Install → write /tmp/my_agent.py → dummy parquet
    │
    └─► Scoring rerun (hidden)
            curl gateway health
            → copy ARC-AGI-3-Agents
            → register MyAgent
            → main.py --agent myagent
            → gateway writes submission.parquet
```

**Design implication:** Track A (plumbing) and Track B (agent score) are separate. Fix Track A before iterating on Track B.

---

## 3. Notebook cell layout (required)

Four code cells, in order:

### 3.1 Install

Install from competition wheels only (no internet):

```python
!pip install --no-index --find-links \
 /kaggle/input/competitions/arc-prize-2026-arc-agi-3/arc_agi_3_wheels \
 arc-agi python-dotenv
```

### 3.2 Write agent

Use `%%writefile /tmp/my_agent.py` — **not** `/kaggle/working/my_agent.py`. Keeping the agent in `/tmp` avoids extra output files in the Submit UI and matches the official starter.

### 3.3 Run / score (rerun branch)

When `KAGGLE_IS_COMPETITION_RERUN` is set:

1. **Health check** — `curl --fail --retry … http://gateway:8001/api/games`
2. **Copy framework** — `cp -r …/ARC-AGI-3-Agents /kaggle/working/`
3. **Install agent** — `cp /tmp/my_agent.py …/agents/templates/my_agent.py`
4. **Register agent** — rewrite `agents/__init__.py` with `'myagent': MyAgent`
5. **Gateway config** — write `.env` with `HOST=gateway`, `PORT=8001`, `OPERATION_MODE=online`
6. **Execute** — `cd …/ARC-AGI-3-Agents && python main.py --agent myagent`

### 3.4 Dummy submission (validation branch)

When **not** rerun:

```python
import pandas as pd
submission = pd.DataFrame(
    data=[['1_0', '1', True, 1]],
    columns=['row_id', 'game_id', 'end_of_game', 'score'])
submission.to_parquet('/kaggle/working/submission.parquet', index=False)
```

**Required columns:** `row_id`, `game_id`, `end_of_game`, `score`.

Do **not** use alternate schemas such as `game_id, score, levels_completed, actions, completed` — Run All may pass, but the end-to-end pipeline expects the starter contract.

---

## 4. Template agent requirements

The agent spliced into `/tmp/my_agent.py` must satisfy:

| Requirement | Rationale |
|-------------|-----------|
| Class named **`MyAgent`** | Framework registration key `'myagent'` |
| Subclass `agents.agent.Agent` | Official agent interface |
| **No** venv bootstrap in agent file | Wheels installed in notebook cell 1 |
| **No** `run_swarm()` in agent file | Scoring runs via `main.py`, not direct Swarm |
| **No** `if __name__ == "__main__"` block | Agent is imported, not executed standalone |
| Implement `choose_action(frames, latest_frame)` | Per-step decision hook |
| Optional `append_frame` post-step hook | Transition logging inside episode |

**Two deployment shapes:**

| Shape | Path | Use |
|-------|------|-----|
| **Kaggle template** | `asra_phaseN_kaggle_template_agent.py` | Competition scoring |
| **Local dev** | `asra_phaseN_my_agent.py` | Swarm, self-test, local episodes |

Only the template form belongs in the Kaggle notebook.

---

## 5. Gateway sidecar configuration

The scoring rerun writes `.env` for the copied framework:

```text
SCHEME=http
HOST=gateway
PORT=8001
ARC_API_KEY=test-key-123
ARC_BASE_URL=http://gateway:8001/
OPERATION_MODE=online
ENVIRONMENTS_DIR=
RECORDINGS_DIR=/kaggle/working/server_recording
```

The sidecar at `http://gateway:8001/` proxies game interaction during scoring. Agents must **not** hardcode the public `three.arcprize.org` endpoint for Kaggle scoring.

Trimmed `agents/__init__.py` pattern:

```python
from typing import Type
from dotenv import load_dotenv
from .agent import Agent, Playback
from .swarm import Swarm
from .templates.random_agent import Random
from .templates.my_agent import MyAgent

load_dotenv()

AVAILABLE_AGENTS: dict[str, Type[Agent]] = {
    'random': Random,
    'myagent': MyAgent,
}
```

---

## 6. Submission artifacts

| Artifact | When | Producer | Notes |
|----------|------|----------|-------|
| `/tmp/my_agent.py` | Both modes | Notebook cell 2 | Not in working output |
| `submission.parquet` | Validation | Notebook cell 4 | Dummy gate row |
| `submission.parquet` | Scoring rerun | Gateway | Real scores |
| `server_recording/` | Scoring rerun | Gateway | Optional replay data |

**Push/submit tooling:** validation runs need only `submission.parquet` in kernel outputs. The agent file lives in `/tmp`.

---

## 7. ASRA shared tooling

ASRA centralizes gateway notebook generation in `kaggle-notebooks/_shared/`:

| Module | Role |
|--------|------|
| `gateway_notebook.py` | Builds 4-cell `.ipynb` from template agent body |
| `phase_registry.py` | Phase 1–9 metadata (agent tag, kernel slug, paths) |
| `extract_template_agent.py` | Extract `MyAgent` subclass from legacy `my_agent.py` |
| `push_and_submit.py` | Kaggle API push + submit with output checks |
| `submit.sh` | Per-phase CLI wrapper |

Rebuild all phase notebooks:

```bash
cd kaggle-notebooks/_shared
./stage0_setup.sh
```

Per-phase submit:

```bash
cd kaggle-notebooks/phaseN
./submit.sh all "asra-vX.X-phaseN v3 official gateway pattern"
```

---

## 8. Migration checklist (Phases 1–9)

Apply before any score-focused iteration:

- [ ] Rebuild notebook via `gateway_notebook.py` (official 4-cell layout)
- [ ] Extract `*_kaggle_template_agent.py` (`MyAgent`, no bootstrap)
- [ ] Dummy gate parquet: `row_id, game_id, end_of_game, score`
- [ ] Agent at `/tmp/my_agent.py`
- [ ] Rerun branch: gateway health → copy → register → `main.py --agent myagent`
- [ ] Submit message includes `v3 official gateway pattern` for traceability
- [ ] Confirm status **Succeeded** (not Kaggle Error) before tuning agent logic

**Verified submissions (ASRA):**

| Phase | Ref | Status | Public score |
|-------|-----|--------|--------------|
| 1 v3 | 53652655 | Succeeded | 0.03 |
| 2 v3 | 53660658 | Succeeded | 0.00 |

Phases 3–9: gateway notebooks rebuilt locally; competition submit pending daily quota.

---

## 9. Common false fixes (do not rely on these alone)

These improvements help local dev but **do not** fix scoring rerun if the gateway path is missing:

| Attempted fix | Why it fails alone |
|---------------|-------------------|
| Move venv to `/tmp` | Scoring still skips gateway |
| Wheels-only install mirror | Same wrong execution path |
| Change dummy parquet column count | Gate may pass; rerun still errors |
| Add `--self-test` in notebook | Validation-only; not scoring contract |
| Direct `run_swarm()` in agent | Not how Kaggle scores |

---

## 10. Parallel: AI Agent Security competition

The same lesson applies across Kaggle agent competitions:

| Competition | Wrong assumption | Correct path |
|-------------|------------------|--------------|
| AI Agent Security | Write `submission.csv` manually | Start inference server; gateway writes CSV on rerun |
| ARC Prize 2026 | Run standalone agent + Swarm | Gateway sidecar + `main.py --agent myagent` |

Always read the **official starter notebook** and match its rerun branch.

---

## 11. References

- [ARC-AGI-3 Kaggle Starter](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter) — canonical evaluation pattern
- [ASRA kaggle-notebooks/_shared](https://github.com/ilakkmanoharan/asra/tree/main/kaggle-notebooks/_shared) — shared builder and submit tooling
- [ASRA Phase 1 kernel](https://www.kaggle.com/code/ilakkmanoharan/asra-phase-1-arc-prize-2026) — reference implementation
- [ASRA Integrated Architecture](https://sci-layer.vercel.app/articles/asra-integrated-architecture) — stack context

---

## 12. One-line takeaway

**Generic Kaggle Error on ARC-AGI-3 usually means the notebook never ran the official gateway evaluation path.** Match the starter's validation/scoring split, register `MyAgent` with the sidecar, and use the official dummy parquet schema — then agent improvements show up in the public score.
