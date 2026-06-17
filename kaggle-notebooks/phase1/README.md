# Phase 1 — Experience Engine (Kaggle & docs)

**Agent tag:** `asra-v0.1-phase1`  
**Competition:** [ARC Prize 2026 — ARC-AGI-3](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3)

| Document | Purpose |
|----------|---------|
| [`asra-phase1-transition-centric-experience.md`](asra-phase1-transition-centric-experience.md) | **Conceptual paper** — theory, architecture, execution fidelity |
| [`phase1-experience-engine.md`](phase1-experience-engine.md) | End-to-end specification + milestone checklist |
| [`phase1-implementation.md`](phase1-implementation.md) | Kaggle + `asra-arc` implementation reference |
| [`asra-phase-1-arc-prize-2026.ipynb`](asra-phase-1-arc-prize-2026.ipynb) | Competition notebook (v4-fixed bootstrap) |

**Kernel:** https://www.kaggle.com/code/ilakkmanoharan/asra-phase-1-arc-prize-2026

## Submissions (archive after each submit)

Immutable snapshots per competition ref: [`submissions/`](submissions/)  
Index: [`../SUBMISSIONS.md`](../SUBMISSIONS.md)

| Ver | Ref | Score | Status |
|-----|-----|-------|--------|
| v3 | 53652655 | **0.03** | COMPLETE |

Working notebook (`asra-phase-1-arc-prize-2026.ipynb`) is the live edit target; `submissions/` freezes what was actually pushed.

---

## Submit via CLI (kagglesdk + access token)

```bash
cd kaggle-notebooks/phase1
export KAGGLE_API_TOKEN="$(cat ~/.kaggle/access_token)"

# Push notebook, Run All on Kaggle, wait, submit
./submit.sh all "asra-v0.1-phase1"

# Or step by step:
./submit.sh push
./submit.sh submit 1 "asra-v0.1-phase1"
```

Shortcut flags via `push_and_submit.py`:

```bash
python3 push_and_submit.py --push-only
python3 push_and_submit.py --skip-push --skip-wait --version 1 --message "asra-v0.1-phase1"
```

---

## What it does

1. Bootstraps dedicated `asra_venv` with competition wheels (v11.4 pattern).
2. Writes **`my_agent.py`** with `ASRAAgent` + semantics inferencer + explorer.
3. Smoke-tests `my_agent.py --self-test` inside venv.
4. Writes **`submission.parquet`** (validation gate).

Scoring re-executes `my_agent.py` — do not rely on notebook kernel for Swarm play.

---

## Notes

- Venv under `/kaggle/working/asra_venv` with `--system-site-packages` for pandas/pyarrow.
- Mirror competition assets into working; resolve `comp_root` from ordered candidates.
- Stub `agents` package — load only `tracing`, `recorder`, `agent`, `swarm`.
- Legacy notebooks: `../asra-phase-1-arc-prize-2026-v4-fixed.ipynb` (same content as this folder).

---

## SciLayer preprint

https://sci-layer.vercel.app/articles/transition-centric-adaptive-reasoning-asra-phase-1 (v3 — Phase 1 parity kernel link)

---

## Last successful submit (parity)

- **Version:** 2 (v2 gate fix — 2026-06-10)  
- **Ref:** 53600233  
- **Message:** `asra-v0.1-phase1 v2 - /tmp venv wheels-only gate fix`  
- **Kernel:** https://www.kaggle.com/code/ilakkmanoharan/asra-phase-1-arc-prize-2026  
- **Fix notes:** `private/error/kaggle-error/arc-resolution.md`

### v1 (failed — Kaggle Error)

- **Ref:** 53474494  
- **Issue:** Full competition tree mirror + venv in `/kaggle/working/asra_venv`

## Prior submissions (historical)

| Ref | Message |
|-----|---------|
| 52998107 | ASRA v0.3 Phase 1 baseline |
| 53226645 | ASRA v11.4 competition venv |

Canonical phase-numbered kernel supersedes these for roadmap parity.

---

## Submissions

See [`submissions/`](submissions/) — gateway v3 ref **53652655**, score **0.03**. Archive new submits with:

```bash
python3 ../_shared/archive_submission.py --phase 1 --version N --ref REF --message "..."
```
