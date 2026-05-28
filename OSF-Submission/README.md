# ASRA — OSF Submission Package

**Project:** [ASRA: Adaptive Scientific Reasoning Architectures](https://osf.io/)  
**Author:** Ilakkuvaselvi Manoharan  
**Repository:** https://github.com/ilakkmanoharan/asra

Upload the folders below to your OSF project (drag each top-level folder into the OSF Files area, or upload as a zip).

---

## Recommended OSF structure

```text
papers/
  asra_paper/              Manuscript (blinded docx + author PDF)
  supplementary_material/  Appendix
  figures/                 Manuscript figures (PNG + combined PDF)

datasets/
  transition_logs/         Phase 1 + large-scale JSONL transition corpora
  exploration_traces/      Episode summaries + state graphs
  replay_datasets/         ARC-AGI-3 replay sample + Kaggle run summary

code/
  asra_phase1/             ASRA v0.1 ARC-AGI-3 codebase (asra-arc)
  arc_experiments/         Decision Biology experiment reports
  notebooks/               Kaggle + analysis notebooks

docs/
  roadmap/                 ASRA roadmap with datasets
  architecture/            ASRA writeup + whitepaper draft
  phase_specifications/    Phase 1 official technical specification

media/
  videos/                  Presentation recordings
  presentations/           Slide outlines + metadata
```

---

## What is included

| Folder | Contents |
|--------|----------|
| **papers** | `asra_for_decision_biology_blinded.docx`, `asra_for_decision_biology_v2.pdf`, appendix, figures 1–5 |
| **datasets** | Exported transition logs, episode CSVs, state graphs, sample replay JSON |
| **code** | Full `asra-arc` source (excludes 549MB LINCS raw + per-episode transition dumps) |
| **docs** | Roadmap, architecture, Phase 1 spec |
| **media** | 3 MP4 videos + presentation metadata |

---

## Not included (too large for OSF — see GitHub)

- `asra-arc/data/decision_biology/lincs/raw/` (~549 MB LINCS signatures)
- `asra-arc/data/large_scale/transitions/` (per-episode JSONL dumps)
- Full Kaggle competition bundle (`arc_agi_3_wheels`, `environment_files`)

Aggregated exports are included under `datasets/`. Full artifacts: https://github.com/ilakkmanoharan/asra

---

## Suggested OSF wiki text

> **ASRA (Adaptive Scientific Reasoning Architecture)** is a research framework for adaptive scientific intelligence — systems that infer hidden action semantics, build world models, and reason through experimentation rather than static prediction alone.
>
> This OSF project contains the manuscript, supplementary appendix, Phase 1 code, transition datasets, technical documentation, and presentation media for the ASRA + Decision Biology research program.

---

## Rebuild this package

```bash
bash OSF-Submission/build_osf_package.sh
```

---

## External links

- **GitHub:** https://github.com/ilakkmanoharan/asra
- **Action semantics video:** https://youtu.be/VmQygZPgK5A
- **ARC Prize 2026:** https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3
