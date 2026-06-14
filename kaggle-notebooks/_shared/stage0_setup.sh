#!/usr/bin/env bash
# Stage 0: extract template agents + rebuild gateway notebooks (no Kaggle submit).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SHARED="$ROOT/_shared"

echo "=== Stage 0: extract template agents (skip existing unless FORCE=1) ==="
EXTRACT_ARGS=(--all)
if [[ "${FORCE:-0}" == "1" ]]; then
  EXTRACT_ARGS+=(--force)
fi
python3 "$SHARED/extract_template_agent.py" "${EXTRACT_ARGS[@]}"

echo "=== Stage 0: rebuild gateway notebooks ==="
python3 "$SHARED/build_phase_notebook.py" --all

echo "=== Done. Notebooks rebuilt locally; no Kaggle push/submit in Stage 0. ==="
