# Kaggle gateway shared tooling (Stage 0)

Official [ARC-AGI-3 Kaggle Starter](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter) pattern — required for scoring. See `private/error/kaggle-error/success.md`.

## When to submit to Kaggle

| Stage | Kaggle submit? | Purpose |
|-------|----------------|---------|
| **0** (this folder) | **No** | Extract template agents, rebuild `.ipynb` locally |
| **1** | **Yes** — one submit per phase | Verify gateway migration (green checkmark, not score) |
| **2** | **Yes** — iterative | Improve Phase 1 agent score |
| **3** | **Yes** — iterative | Phase 9 as primary score-chasing kernel |

## Commands

```bash
# Stage 0 — local only (no Kaggle)
./kaggle-notebooks/_shared/stage0_setup.sh

# Extract one phase template (skip if exists)
python3 kaggle-notebooks/_shared/extract_template_agent.py --phase 3 --force

# Rebuild notebook(s)
python3 kaggle-notebooks/_shared/build_phase_notebook.py --phase 3
python3 kaggle-notebooks/_shared/build_phase_notebook.py --all

# Stage 1+ — push + submit (from repo root)
python3 kaggle-notebooks/_shared/push_and_submit.py --phase 3
python3 kaggle-notebooks/_shared/push_and_submit.py --phase 3 --push-only
python3 kaggle-notebooks/_shared/push_and_submit.py --phase 3 --skip-push --skip-wait --version 2 --message "asra-v0.5-phase3 v3 official gateway pattern"
```

## Files

| File | Role |
|------|------|
| `phase_registry.py` | Phase metadata (kernel slug, paths, agent tags) |
| `gateway_notebook.py` | Build official-pattern notebook JSON |
| `extract_template_agent.py` | Strip bootstrap/Swarm from `my_agent.py` → template |
| `build_phase_notebook.py` | CLI to rebuild `.ipynb` |
| `push_and_submit.py` | Kaggle SDK push + wait + submit |
| `stage0_setup.sh` | Extract all + rebuild all (no submit) |

## Agent file pairs

| Local dev | Kaggle scoring |
|-----------|----------------|
| `asra_phaseN_my_agent.py` | `asra_phaseN_kaggle_template_agent.py` |
| Swarm + bootstrap | `MyAgent` subclass, no `__main__` |

Edit `my_agent.py` for local work → re-extract template → rebuild notebook → submit (Stage 1+).
