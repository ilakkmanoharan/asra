# Kaggle submission archive

**Location:** `kaggle-notebooks/phaseN/submissions/v{kernel_ver}-ref{submission_ref}/`

Create an archive folder **only after** a competition submit returns a ref. Do not pre-create for phases not yet submitted.

## Per-submission folder contents

| File | When | Purpose |
|------|------|---------|
| `notebook.ipynb` | On submit | Exact notebook pushed to Kaggle |
| `template-agent.py` | On submit | `MyAgent` source spliced into notebook cell 2 |
| `theory-source.md` | On submit | Copy of phase concept paper from parent folder |
| `theory.md` | On submit | What this specific submit implements |
| `submission-log.json` | On submit | Machine-readable ref, version, status, score |
| `submission-log.md` | On submit | Human-readable submit record |
| `testing.md` | On submit | Pre-submit checks + validation/scoring checklist |
| `log-analysis.md` | After scoring | Track A/B analysis, root cause if ERROR |
| `next-submission-plan.md` | After scoring | Pointer to next UTC-day submit |

## Workflow

```bash
# 1. Submit
cd kaggle-notebooks/phaseN
./submit.sh all "asra-vX-phaseN v3 official gateway pattern"
# Note kernel VERSION and ref from output

# 2. Archive immediately (PENDING)
python3 kaggle-notebooks/_shared/archive_submission.py \
  --phase N --version VERSION --ref REF \
  --message "asra-vX-phaseN v3 official gateway pattern"

# 3. After Kaggle shows Succeeded/ERROR + score
python3 kaggle-notebooks/_shared/archive_submission.py \
  --phase N --version VERSION --ref REF \
  --update-status COMPLETE --update-score 0.00
# Then edit log-analysis.md and theory.md if needed
```

## Index by phase

| Phase | Submissions | Best score |
|-------|-------------|------------|
| 1 | [phase1/submissions/](phase1/submissions/) | **0.03** (v3 ref 53652655) |
| 2 | [phase2/submissions/](phase2/submissions/) | 0.00 (v5 ref 53660658) |
| 3 | [phase3/submissions/](phase3/submissions/) | 0.00 (v2 ref 53720818) |
| 4 | [phase4/submissions/](phase4/submissions/) | 0.00 (v4 ref 53760137) |
| 5 | [phase5/submissions/](phase5/submissions/) | *not submitted* |
| 6 | [phase6/submissions/](phase6/submissions/) | *not submitted* |
| 7 | [phase7/submissions/](phase7/submissions/) | *not submitted* |
| 8 | [phase8/submissions/](phase8/submissions/) | *not submitted* |
| 9 | [phase9/submissions/](phase9/submissions/) | *not submitted* |

## Calendar & planning

Daily calendar: [`../private/next-steps/kaggle/README.md`](../private/next-steps/kaggle/README.md)  
**Today:** [`TODAY.md`](TODAY.md)

**Rule:** 1 competition submit per UTC day. Working notebooks in `phaseN/` evolve; `submissions/` is immutable history per ref.
