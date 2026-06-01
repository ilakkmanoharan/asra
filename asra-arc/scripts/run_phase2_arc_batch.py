#!/usr/bin/env python3
"""Batch-run Phase 2 perception over an ARC task directory."""

from __future__ import annotations

import argparse
from pathlib import Path

from asra.perception import run_phase2_batch


def main() -> None:
    p = argparse.ArgumentParser(description="ASRA Phase 2 — ARC before/after analysis")
    p.add_argument(
        "--arc-root",
        default="data/arc/original/training",
        help="Root folder of ARC tasks (subdirs with task JSON)",
    )
    p.add_argument(
        "--output-dir",
        default="data/analysis/phase2/reports",
        help="Where to write per-task JSON reports",
    )
    args = p.parse_args()
    paths = run_phase2_batch(args.arc_root, args.output_dir)
    print(f"Reports: {len(paths)} -> {args.output_dir}")


if __name__ == "__main__":
    main()
