#!/usr/bin/env python3
"""Compare ASRA TransformationDetector labels with scripted grid deltas (ARCLE optional)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from asra.perception.transforms import TransformationDetector


def _dominant_event_class(detection) -> str:
    if not detection.events:
        return "IDENTITY"
    counts: dict[str, int] = {}
    for e in detection.events:
        counts[e.transform_class.value] = counts.get(e.transform_class.value, 0) + 1
    return max(counts, key=counts.get)


def synthetic_cases() -> list[dict[str, Any]]:
    """Small grids where expected dominant transform is unambiguous."""
    return [
        {
            "name": "identity",
            "before": [[0, 0], [0, 0]],
            "after": [[0, 0], [0, 0]],
            "expected": "IDENTITY",
        },
        {
            "name": "create_blob",
            "before": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            "after": [[0, 1, 0], [0, 1, 0], [0, 0, 0]],
            "expected": "CREATE",
        },
        {
            "name": "delete_blob",
            "before": [[0, 0, 0], [0, 2, 0], [0, 0, 0]],
            "after": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            "expected": "DELETE",
        },
        {
            "name": "translate_blob",
            "before": [[0, 0, 0], [0, 3, 0], [0, 0, 0]],
            "after": [[0, 0, 0], [0, 0, 0], [0, 3, 0]],
            "expected": "TRANSLATE",
        },
    ]


def run_synthetic(detector: TransformationDetector) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in synthetic_cases():
        det = detector.detect_grids(case["before"], case["after"])
        got = _dominant_event_class(det)
        rows.append(
            {
                "case": case["name"],
                "expected": case["expected"],
                "got": got,
                "summary": det.summary,
                "pass": got == case["expected"],
            }
        )
    return rows


def run_arcle_probe() -> dict[str, Any] | None:
    try:
        import gymnasium as gym  # noqa: F401
        import arcle  # noqa: F401
    except ImportError as exc:
        return {"available": False, "reason": str(exc)}

    import gymnasium as gym
    import arcle  # noqa: F401

    probe: dict[str, Any] = {"available": True, "envs_tried": []}
    for env_id in ("O2ARCEnv-v0", "RawARCEnv-v0"):
        try:
            env = gym.make(env_id)
            ops = getattr(env.unwrapped, "create_operations", None)
            op_names: list[str] = []
            if callable(ops):
                created = ops()
                if isinstance(created, dict):
                    op_names = sorted(str(k) for k in created.keys())
                elif isinstance(created, (list, tuple)):
                    op_names = [getattr(o, "__name__", str(o)) for o in created]
            probe["envs_tried"].append({"env_id": env_id, "operation_names": op_names[:30]})
            env.close()
        except Exception as err:  # noqa: BLE001
            probe["envs_tried"].append({"env_id": env_id, "error": str(err)})
    return probe


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="data/analysis/phase2/arcle_validation.json")
    args = p.parse_args()

    detector = TransformationDetector()
    synthetic = run_synthetic(detector)
    arcle_probe = run_arcle_probe()

    report = {
        "synthetic": synthetic,
        "synthetic_pass_rate": sum(1 for r in synthetic if r["pass"]) / max(len(synthetic), 1),
        "arcle": arcle_probe,
        "notes": (
            "Synthetic cases validate ASRA object-level detector on controlled grids. "
            "ARCLE probe lists env operation names when arcle+gymnasium are installed; "
            "full step-by-step parity with ARCLE ops is future work."
        ),
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    passed = sum(1 for r in synthetic if r["pass"])
    print(f"Synthetic: {passed}/{len(synthetic)} passed")
    if arcle_probe and arcle_probe.get("available"):
        print("ARCLE: installed — env probe recorded")
    else:
        print(f"ARCLE: not installed ({arcle_probe.get('reason') if arcle_probe else 'n/a'})")
    print(f"Wrote {out}")
    return 0 if passed == len(synthetic) else 1


if __name__ == "__main__":
    sys.exit(main())
