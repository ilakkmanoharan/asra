# Phase 3 — Exploration, Memory, and Navigation

**Timeline:** July 2026  
**Status:** **COMPLETE** — Milestones 3A–3D + Kaggle notebook  
**Implementation:** `asra-arc/src/asra/exploration/`  
**Agent tag:** `asra-v0.5-phase3`

---

## Documents in this folder

| Document | Role |
|----------|------|
| **[asra-phase3-exploration-memory-navigation.md](asra-phase3-exploration-memory-navigation.md)** | **Conceptual article** — theory & architecture (companion to notebook) |
| **[phase3-implementation.md](phase3-implementation.md)** | **Implementation reference** — modules, CLI, scripts, tests |
| **[phase3-exploration-memory-navigation.md](phase3-exploration-memory-navigation.md)** | **Detailed specification** — milestones, schemas, metrics |
| **[asra-phase-3-arc-prize-2026.ipynb](asra-phase-3-arc-prize-2026.ipynb)** | **Kaggle submission notebook** |
| Phase 2 (complete) | [`../phase2/asra-phase2-object-centric-reasoning.md`](../phase2/asra-phase2-object-centric-reasoning.md) |

---

## Kaggle submission (ARC Prize 2026)

| File | Purpose |
|------|---------|
| [`asra-phase-3-arc-prize-2026.ipynb`](asra-phase-3-arc-prize-2026.ipynb) | Competition notebook — writes `my_agent.py` + `submission.parquet` |
| [`asra_phase3_my_agent.py`](asra_phase3_my_agent.py) | Source agent (Phase 2 object hints + Phase 3 exploration memory) |
| [`kernel-metadata.json`](kernel-metadata.json) | Kaggle kernel metadata |
| [`push_and_submit.py`](push_and_submit.py) | Push + Run All + submit via kagglesdk |
| [`submit.sh`](submit.sh) | Shortcut: `./submit.sh all` |

**Kernel slug:** `ilakkmanoharan/asra-phase-3-arc-prize-2026`  
**Competition:** `arc-prize-2026-arc-agi-3`

### Regenerate notebook after editing the agent

```bash
cd asra-arc
python scripts/build_phase3_kaggle_notebook.py
```

### Local smoke test (no competition data)

```bash
python kaggle-notebooks/phase3/asra_phase3_my_agent.py --self-test
```

### Submit via CLI

```bash
cd kaggle-notebooks/phase3
export KAGGLE_API_TOKEN="$(cat ~/.kaggle/access_token)"

python3 push_and_submit.py --message "ASRA v0.5-phase3 exploration memory hints"
# or
./submit.sh all
```

**Notes (same as Phase 2):**
- Venv at **`/tmp/asra_venv`** on Kaggle (not `/kaggle/working`) — avoids 500-file output cap
- Do not mirror `ARC-AGI-3-Agents` into working; use competition input paths
- Scoring re-runs `my_agent.py` in the venv — Swarm is **not** executed in the notebook

## Last successful submit

- **Kernel:** https://www.kaggle.com/code/ilakkmanoharan/asra-phase-3-arc-prize-2026
- **Version:** 1
- **Competition ref:** 53270909
- **Message:** ASRA v0.5-phase3 exploration memory hints

---

## Library quick start (offline)

```bash
cd asra-arc
pip install -e '.[dev,exploration]'

python -m asra run-minigrid --env MiniGrid-DoorKey-8x8-v0 --episodes 20 --max-steps 300
python -m asra run-babyai --env BabyAI-GoToRedBallGrey-v0 --episodes 10
python -m asra run-arc-exploration --mock --max-steps 50
python -m asra eval-doorkey --episodes 20

python scripts/eval_phase3_babyai.py
python scripts/eval_phase3_arc_ablation.py
```

Full library reference: **[phase3-implementation.md](phase3-implementation.md)**.

---

## Deliverables checklist

| # | Deliverable | Status |
|---|-------------|--------|
| 1–11 | Library modules (exploration engine) | ✅ — see implementation doc |
| 12 | Kaggle Phase 3 notebook + agent | ✅ — this folder |
| 13 | Push/submit tooling | ✅ — `push_and_submit.py`, `submit.sh` |
