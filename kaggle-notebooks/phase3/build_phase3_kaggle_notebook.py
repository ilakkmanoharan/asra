#!/usr/bin/env python3
"""Build Kaggle Phase 3 notebook (delegates to _shared gateway builder)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
from gateway_notebook import build_and_write
from phase_registry import get_phase


def main() -> None:
    out = build_and_write(get_phase(3))
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
