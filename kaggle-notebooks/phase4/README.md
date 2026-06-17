# Phase 4 — Action Semantics and Causal Inference

**Timeline:** July → August 2026  
**Status:** **IN PROGRESS** — Milestones 4A, 4B, 4D complete; PHYRE (4C) pending  
**Agent tag:** `asra-v0.6-phase4`  
**Depends on:** Phase 1 ✅, Phase 2 ✅, Phase 3 ✅

---

## Documents

| Document | Role |
|----------|------|
| **[phase4-action-semantics-causal-inference.md](phase4-action-semantics-causal-inference.md)** | Full specification |
| **[phase4-implementation.md](phase4-implementation.md)** | Implementation reference (modules, CLI, Kaggle) |
| **[asra-phase4-action-semantics-causal-inference.md](asra-phase4-action-semantics-causal-inference.md)** | **Conceptual article** (companion to Kaggle notebook) |

## Submissions

Archive after each competition submit: [`submissions/`](submissions/)

| Ver | Ref | Score | Status |
|-----|-----|-------|--------|
| v3 | 53755707 | — | ERROR (missing `CausalSemanticsEngine`) |
| v4 | 53760137 | **0.00** | **Succeeded** |

---

## Kaggle submission

| File | Role |
|------|------|
| `asra-phase-4-arc-prize-2026.ipynb` | Submit notebook |
| `asra_phase4_my_agent.py` | Source agent (embedded in notebook as `my_agent.py`) |
| `setup_kaggle_cli.sh` | One-time: create `~/.kaggle/kaggle.json` from `access_token` |
| `submit.sh` | Push + submit via kagglesdk (`access_token`) |
| `push_and_submit.py` | Same as `submit.sh` (Python) |

### One-time CLI setup (KGAT access token)

Your `~/.kaggle/access_token` (KGAT) works as the legacy API **key** when paired with your username:

```bash
./setup_kaggle_cli.sh
# writes ~/.kaggle/kaggle.json (chmod 600)
```

Or use environment variables (no `kaggle.json` file):

```bash
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
export KAGGLE_USERNAME="ilakkmanoharan"
export KAGGLE_KEY="$(cat ~/.kaggle/access_token)"
```

### Submit via `kaggle` CLI

```bash
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
cd kaggle-notebooks/phase4

# Rebuild notebook after editing asra_phase4_my_agent.py
python3 ../../asra-arc/scripts/build_phase4_kaggle_notebook.py

# Self-test locally
python3 asra_phase4_my_agent.py --self-test

# Push notebook (creates new kernel version)
kaggle kernels push -p .

# Wait until Run All completes on Kaggle, then submit (use latest version number)
kaggle kernels status ilakkmanoharan/asra-phase-4-arc-prize-2026
kaggle competitions submit arc-prize-2026-arc-agi-3 \
  -k ilakkmanoharan/asra-phase-4-arc-prize-2026 \
  -v 2 \
  -m "ASRA v0.6-phase4 causal semantics"
```

`kernels push` uploads sources only; open the kernel on Kaggle and **Run All** (or use `push_and_submit.py` below, which pushes and runs automatically).

### Submit via kagglesdk (recommended for Run All + wait)

```bash
export KAGGLE_API_TOKEN="$(cat ~/.kaggle/access_token)"
./submit.sh all "ASRA v0.6-phase4 causal semantics"
```

---

## Library

```text
asra-arc/src/asra/causality/
  effect_summarizer.py    transition_model.py    hypothesis_tester.py
  counterfactual.py       uncertainty.py         change_analyzer.py
  semantics_store.py      arc_semantics.py       policy_v3.py
```

**Tests:** 67 passing (`tests/test_causality.py` + prior phases)

---

## What Phase 4 adds to the agent

| Layer | Capability |
|-------|------------|
| Phase 2 | Object-scene hints |
| Phase 3 | Visit memory, novelty, exploration |
| **Phase 4** | Semantic labels, confidence, uncertainty, transition prediction, counterfactual lookup |

Reasoning string example:

```text
ASRA Phase4: ACTION3 | objects=5 | visits=2 | sem=translate conf=0.81 u=0.12
```
