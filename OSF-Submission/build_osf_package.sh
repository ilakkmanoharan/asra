#!/usr/bin/env bash
# Build OSF upload package from repo sources.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OSF="$ROOT/OSF-Submission"

echo "Building OSF package at $OSF"

# Clean prior build (keep this script + README)
for item in papers datasets code docs media; do
  rm -rf "$OSF/$item"
done

mkdir -p "$OSF"/{papers/{asra_paper,supplementary_material,figures},datasets/{transition_logs,exploration_traces,replay_datasets},code/{asra_phase1,arc_experiments,notebooks},docs/{roadmap,architecture,phase_specifications},media/{videos,presentations}}

# --- papers ---
cp "$ROOT/paper/asra_for_decision_biology_blinded.docx" "$OSF/papers/asra_paper/"
cp "$ROOT/paper/asra_for_decision_biology_v2.pdf" "$OSF/papers/asra_paper/"
cp "$ROOT/paper/asra_for_decision_biology_appendix.docx" "$OSF/papers/supplementary_material/"
cp "$ROOT/private/Patterns/v5/figures/"*.png "$OSF/papers/figures/" 2>/dev/null || true
cp "$ROOT/private/entropy/manuscript_figures.pdf" "$OSF/papers/figures/" 2>/dev/null || true

# --- datasets ---
cp "$ROOT/asra-arc/data/exports/asra_v0_1_transitions.jsonl" "$OSF/datasets/transition_logs/"
cp "$ROOT/asra-arc/data/large_scale/exports/asra_v0_1_transitions.jsonl" "$OSF/datasets/transition_logs/asra_v0_1_large_scale_transitions.jsonl"
cp "$ROOT/kaggle-dataset/asra_v0_2_transition_log.jsonl" "$OSF/datasets/transition_logs/" 2>/dev/null || true
cp "$ROOT/asra-arc/data/exports/asra_v0_1_episode_summary.csv" "$OSF/datasets/exploration_traces/"
cp "$ROOT/asra-arc/data/large_scale/exports/asra_v0_1_episode_summary.csv" "$OSF/datasets/exploration_traces/asra_v0_1_large_scale_episode_summary.csv"
cp "$ROOT/asra-arc/data/exports/asra_v0_1_state_graph.json" "$OSF/datasets/exploration_traces/"
cp "$ROOT/asra-arc/data/large_scale/exports/asra_v0_1_state_graph.json" "$OSF/datasets/exploration_traces/asra_v0_1_large_scale_state_graph.json"
cp "$ROOT/asra-arc/data/raw/sample_arc_agi3_replay.json" "$OSF/datasets/replay_datasets/"
cp "$ROOT/kaggle-dataset/asra_v0_2_summary.json" "$OSF/datasets/replay_datasets/" 2>/dev/null || true

# --- code: asra-arc (no bulky raw LINCS or per-episode transition dumps) ---
rsync -a --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='.pytest_cache' \
  --exclude='data/large_scale/transitions' \
  --exclude='data/decision_biology/lincs/raw' \
  --exclude='data/decision_biology/omnipath/transitions' \
  "$ROOT/asra-arc/" "$OSF/code/asra_phase1/"

cp "$ROOT/kaggle-notebooks/"*.ipynb "$OSF/code/notebooks/"
cp "$ROOT/asra-arc/notebooks/"*.ipynb "$OSF/code/notebooks/"

# ARC / Decision Biology experiment summaries
mkdir -p "$OSF/code/arc_experiments/decision_biology"
cp "$ROOT/asra-arc/data/decision_biology/omnipath/documents/"*.md "$OSF/code/arc_experiments/decision_biology/" 2>/dev/null || true
cp "$ROOT/asra-arc/data/decision_biology/analysis/decision_biology_combined_report.json" "$OSF/code/arc_experiments/" 2>/dev/null || true

# --- docs ---
cp "$ROOT/private/documents/ASRA-theory/ASRA-roadmap-datasets.md" "$OSF/docs/roadmap/"
cp "$ROOT/documents/ASRA-writeup.md" "$OSF/docs/architecture/"
cp "$ROOT/documents/ASRA_Phase1_Official_Technical_Specification.md" "$OSF/docs/phase_specifications/"
cp "$ROOT/documents/asra_decision_biology_whitepaper_nature_style.md" "$OSF/docs/architecture/" 2>/dev/null || true

# --- media ---
cp "$ROOT/videos/"*.mp4 "$OSF/media/videos/"
cp "$ROOT/private/video-making/asra-1/slides.md" "$OSF/media/presentations/" 2>/dev/null || true
cp "$ROOT/private/video-making/asra-1/meta-data.md" "$OSF/media/presentations/" 2>/dev/null || true
cp "$ROOT/private/video-making/NFM-DecisionBiology-ASRA/metadata.md" "$OSF/media/presentations/" 2>/dev/null || true

echo "Done. Package size:"
du -sh "$OSF"
