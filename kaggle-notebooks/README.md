# ASRA Kaggle notebooks (Phases 1–9)

Competition lane for [ARC Prize 2026 — ARC-AGI-3](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3). Each phase has a dedicated folder with notebook, conceptual paper, submit CLI, and README.

**Submission archive:** [`SUBMISSIONS.md`](SUBMISSIONS.md) — per-ref snapshots under `phaseN/submissions/` (created **only after** each competition submit).

| Phase | Agent tag | Folder | Kernel |
|-------|-----------|--------|--------|
| 1 | `asra-v0.1-phase1` | [phase1/](phase1/) | [asra-phase-1-arc-prize-2026](https://www.kaggle.com/code/ilakkmanoharan/asra-phase-1-arc-prize-2026) |
| 2 | `asra-v0.4-phase2` | [phase2/](phase2/) | [asra-phase-2-arc-prize-2026](https://www.kaggle.com/code/ilakkmanoharan/asra-phase-2-arc-prize-2026) |
| 3 | `asra-v0.5-phase3` | [phase3/](phase3/) | [asra-phase-3-arc-prize-2026](https://www.kaggle.com/code/ilakkmanoharan/asra-phase-3-arc-prize-2026) |
| 4 | `asra-v0.6-phase4` | [phase4/](phase4/) | [asra-phase-4-arc-prize-2026](https://www.kaggle.com/code/ilakkmanoharan/asra-phase-4-arc-prize-2026) |
| 5 | `asra-v0.7-phase5` | [phase5/](phase5/) | [asra-phase-5-arc-prize-2026](https://www.kaggle.com/code/ilakkmanoharan/asra-phase-5-arc-prize-2026) |
| 6 | `asra-v0.8-phase6` | [phase6/](phase6/) | [asra-phase-6-arc-prize-2026](https://www.kaggle.com/code/ilakkmanoharan/asra-phase-6-arc-prize-2026) |
| 7 | `asra-v0.85-phase7` | [phase7/](phase7/) | [asra-phase-7-arc-prize-2026](https://www.kaggle.com/code/ilakkmanoharan/asra-phase-7-arc-prize-2026) |
| 8 | `asra-v0.9-phase8` | [phase8/](phase8/) | [asra-phase-8-arc-prize-2026](https://www.kaggle.com/code/ilakkmanoharan/asra-phase-8-arc-prize-2026) |
| 9 | `asra-v1.0-phase9` | [phase9/](phase9/) | [asra-phase-9-arc-prize-2026](https://www.kaggle.com/code/ilakkmanoharan/asra-phase-9-arc-prize-2026) |

## Submit pattern (Stage 1+)

**Stage 0 does not submit** — it only extracts template agents and rebuilds notebooks locally.

```bash
# Stage 0 — local only
./kaggle-notebooks/_shared/stage0_setup.sh

# Stage 1+ — push + submit (gateway pattern required)
cd kaggle-notebooks/phaseN
./submit.sh all "asra-vX-phaseN v3 official gateway pattern"

# Or from anywhere:
python3 kaggle-notebooks/_shared/push_and_submit.py --phase N
```

If `GetKernelSessionStatus` returns HTTP 500:

```bash
./submit.sh push
sleep 900
./submit.sh submit VERSION "asra-vX-phaseN v3 official gateway pattern"
```

See [`_shared/README.md`](_shared/README.md) for full tooling docs.

## SciLayer preprints

https://sci-layer.vercel.app/articles — Phase 1–9 manuscripts + technical specs.

| Spec | Local copy |
|------|------------|
| [Gateway deployment](https://sci-layer.vercel.app/articles/arc-agi-3-kaggle-gateway-deployment-spec) | [`documents/specs/arc-agi-3-kaggle-gateway-deployment-spec.md`](../documents/specs/arc-agi-3-kaggle-gateway-deployment-spec.md) |
| [Repeated-run eval](https://sci-layer.vercel.app/articles/asra-repeated-run-eval-arc-agi-3) | [`documents/specs/asra-repeated-run-eval-arc-agi-3.md`](../documents/specs/asra-repeated-run-eval-arc-agi-3.md) |
| [Integrated architecture](https://sci-layer.vercel.app/articles/asra-integrated-architecture) | [`documents/architecture/asra-integrated-architecture.md`](../documents/architecture/asra-integrated-architecture.md) |
| [Evaluation Report v0](https://sci-layer.vercel.app/articles/asra-arc-agi-3-evaluation-report-v0) | [`documents/evaluation/asra-arc-agi-3-evaluation-report-v0.md`](../documents/evaluation/asra-arc-agi-3-evaluation-report-v0.md) |
| [Phase 2 ARC results](https://sci-layer.vercel.app/articles/asra-phase-2-original-arc-evaluation-results) | [`documents/evaluation/asra-phase-2-original-arc-evaluation-results.md`](../documents/evaluation/asra-phase-2-original-arc-evaluation-results.md) |

Archived notebooks: [SciLayer/content/kaggle-notebooks](https://github.com/ilakkmanoharan/SciLayer/tree/main/content/kaggle-notebooks).

## Legacy root notebooks

- `asra-phase-1-arc-prize-2026-v4-fixed.ipynb` — superseded by `phase1/asra-phase-1-arc-prize-2026.ipynb`
- `asra_v0_1_phase1_arc_agi3_notebook.ipynb`, `asra_v0_2_phase1_arc_agi3_notebook.ipynb` — early Phase 1 iterations
