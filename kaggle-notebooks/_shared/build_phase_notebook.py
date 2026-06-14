#!/usr/bin/env python3
"""Build gateway-pattern Kaggle notebook(s) for one or more phases."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gateway_notebook import build_and_write
from phase_registry import PHASES


def main() -> None:
    p = argparse.ArgumentParser(description="Build ARC gateway Kaggle notebook(s)")
    p.add_argument("--phase", type=int, action="append", dest="phases")
    p.add_argument("--all", action="store_true")
    p.add_argument("--accelerator", default="cpu", choices=["cpu", "t4"])
    args = p.parse_args()

    numbers = sorted(PHASES) if args.all else (args.phases or [])
    if not numbers:
        p.error("Specify --phase N and/or --all")

    for n in numbers:
        phase = PHASES[n]
        out = build_and_write(phase, accelerator=args.accelerator)
        print(f"Phase {n}: wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
