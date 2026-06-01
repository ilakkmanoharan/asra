#!/usr/bin/env bash
# Phase 2 Kaggle submit helpers (uses kagglesdk + ~/.kaggle/access_token)
set -euo pipefail
cd "$(dirname "$0")"
export KAGGLE_API_TOKEN="${KAGGLE_API_TOKEN:-$(cat ~/.kaggle/access_token)}"

case "${1:-all}" in
  push)
    python3 push_and_submit.py --push-only
    ;;
  submit)
    python3 push_and_submit.py --skip-push --skip-wait --version "${2:-1}"
    ;;
  all)
    python3 push_and_submit.py --message "${2:-ASRA v0.4-phase2}"
    ;;
  *)
    echo "Usage: $0 {push|submit VERSION|all [message]}"
    exit 1
    ;;
esac
