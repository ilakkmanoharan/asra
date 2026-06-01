# Phase 2 Kaggle submission

**Concept article:** [`asra-phase2-object-centric-reasoning.md`](asra-phase2-object-centric-reasoning.md) — theory, architecture, and Phase 1→2 bridge (no submission/env how-to).

**Notebook:** `asra-phase-2-arc-prize-2026.ipynb`  
**Kernel:** https://www.kaggle.com/code/ilakkmanoharan/asra-phase-2-arc-prize-2026  
**Competition:** `arc-prize-2026-arc-agi-3`

## Submit via CLI (kagglesdk + access token)

Uses `~/.kaggle/access_token` (KGAT), same as Phase 1 v11-4.

```bash
cd kaggle-notebooks/phase2
export KAGGLE_API_TOKEN="$(cat ~/.kaggle/access_token)"

# Push notebook, Run All on Kaggle, wait, submit
python3 push_and_submit.py --message "ASRA v0.4-phase2"

# Or step by step:
python3 push_and_submit.py --push-only          # push + wait only
python3 push_and_submit.py --skip-push --version 3 --message "..."  # submit existing version
```

Shortcut: `./submit.sh all`

## Legacy `kaggle` CLI (needs kaggle.json)

```bash
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
kaggle kernels push -p kaggle-notebooks/phase2
kaggle competitions submit arc-prize-2026-arc-agi-3 \
  -f submission.parquet \
  -k ilakkmanoharan/asra-phase-2-arc-prize-2026 \
  -v 3 \
  -m "ASRA v0.4-phase2"
```

## Notes

- Venv is created under **`/tmp/asra_venv`** on Kaggle (not `/kaggle/working`) so outputs stay under the 500-file cap.
- Do not mirror `ARC-AGI-3-Agents` into working; use competition input paths directly.

## Last successful submit

- **Version:** 4  
- **Ref:** 53268471  
- **Message:** ASRA v0.4-phase2 resubmit
