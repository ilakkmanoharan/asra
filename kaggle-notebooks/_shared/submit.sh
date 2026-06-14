#!/usr/bin/env bash
# Push/submit gateway notebook for a phase (Stage 1+).
set -euo pipefail
PHASE="${1:?Usage: submit.sh PHASE [push|submit VERSION [message]|all [message]]}"
shift
ROOT="$(cd "$(dirname "$0")" && pwd)"
SHARED="$ROOT/../_shared"
export KAGGLE_API_TOKEN="${KAGGLE_API_TOKEN:-$(cat ~/.kaggle/access_token 2>/dev/null || true)}"

case "${1:-all}" in
  push)
    python3 "$SHARED/push_and_submit.py" --phase "$PHASE" --push-only
    ;;
  submit)
    python3 "$SHARED/push_and_submit.py" --phase "$PHASE" --skip-push --skip-wait \
      --version "${2:-1}" --message "${3:-}"
    ;;
  all)
    python3 "$SHARED/push_and_submit.py" --phase "$PHASE" --message "${2:-}"
    ;;
  *)
    echo "Usage: $0 PHASE {push|submit VERSION [message]|all [message]}"
    exit 1
    ;;
esac
