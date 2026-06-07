#!/usr/bin/env bash
# Configure legacy `kaggle` CLI from ~/.kaggle/access_token (KGAT).
# Does not commit secrets; writes only to ~/.kaggle/kaggle.json
set -euo pipefail

TOKEN_FILE="${KAGGLE_TOKEN_FILE:-$HOME/.kaggle/access_token}"
OUT="${KAGGLE_CONFIG:-$HOME/.kaggle/kaggle.json}"
USERNAME="${KAGGLE_USERNAME:-ilakkmanoharan}"

if [[ ! -f "$TOKEN_FILE" ]]; then
  echo "Missing token file: $TOKEN_FILE" >&2
  echo "Create it from https://www.kaggle.com/settings (API → Generate New Token)" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"
python3 - "$USERNAME" "$TOKEN_FILE" "$OUT" <<'PY'
import json
import sys

username, token_path, out_path = sys.argv[1:4]
key = open(token_path, encoding="utf-8").read().strip()
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"username": username, "key": key}, f)
    f.write("\n")
PY

chmod 600 "$OUT"
echo "Wrote $OUT (mode 600)"
echo "Test: export PATH=\"\$HOME/Library/Python/3.9/bin:\$PATH\" && kaggle kernels status ${USERNAME}/asra-phase-4-arc-prize-2026"
