#!/usr/bin/env python3
"""Aggregate Phase 2 perception reports into evaluation metrics."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def _load_reports(report_dir: Path) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for path in sorted(report_dir.glob("*.json")):
        try:
            reports.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return reports


def summarize(reports: list[dict[str, Any]]) -> dict[str, Any]:
    n_tasks = len(reports)
    n_with_rules = sum(1 for r in reports if r.get("rule_candidates"))
    top_rule_coverage = sum(
        1
        for r in reports
        if r.get("rule_candidates") and r["rule_candidates"][0].get("confidence", 0) >= 1.0
    )
    branched_tasks = sum(
        1
        for r in reports
        if r.get("rule_candidates") and r["rule_candidates"][0].get("pattern") == "BRANCHED_PER_DEMO"
    )
    transform_counts: Counter[str] = Counter()
    object_counts: list[int] = []
    event_counts: list[int] = []
    errors = 0

    for r in reports:
        for pair in r.get("pair_reports", []):
            object_counts.append(len(pair.get("input_scene", {}).get("objects", [])))
            events = pair.get("transform", {}).get("events", [])
            event_counts.append(len(events))
            for ev in events:
                transform_counts[ev.get("transform_class", "UNKNOWN")] += 1

    avg_objects = sum(object_counts) / len(object_counts) if object_counts else 0.0
    avg_events = sum(event_counts) / len(event_counts) if event_counts else 0.0

    return {
        "num_tasks": n_tasks,
        "num_with_rule_candidates": n_with_rules,
        "pct_with_rule_candidates": round(100.0 * n_with_rules / n_tasks, 2) if n_tasks else 0.0,
        "num_common_rule_coverage": top_rule_coverage,
        "pct_common_rule_coverage": round(100.0 * top_rule_coverage / n_tasks, 2) if n_tasks else 0.0,
        "num_branched_per_demo": branched_tasks,
        "pct_branched_per_demo": round(100.0 * branched_tasks / n_tasks, 2) if n_tasks else 0.0,
        "avg_objects_per_input_scene": round(avg_objects, 3),
        "avg_transform_events_per_pair": round(avg_events, 3),
        "transform_event_distribution": dict(transform_counts.most_common()),
        "parse_errors": errors,
    }


def list_exceptions(reports: list[dict[str, Any]], limit: int = 20) -> list[str]:
    ids: list[str] = []
    for r in reports:
        rules = r.get("rule_candidates") or []
        if not rules or rules[0].get("confidence", 0) < 1.0:
            ids.append(str(r.get("task_id", "unknown")))
    return ids[:limit]


def main() -> None:
    p = argparse.ArgumentParser(description="Summarize Phase 2 ARC batch reports")
    p.add_argument("--report-dir", required=True)
    p.add_argument("--output", default="data/analysis/phase2/summary.json")
    p.add_argument("--label", default="dataset")
    p.add_argument("--list-exceptions", action="store_true")
    args = p.parse_args()

    report_dir = Path(args.report_dir)
    reports = _load_reports(report_dir)
    if args.list_exceptions:
        for tid in list_exceptions(reports, limit=50):
            print(tid)
        return

    summary = summarize(reports)
    summary["exception_task_ids"] = list_exceptions(reports, limit=50)
    summary["label"] = args.label
    summary["report_dir"] = str(report_dir)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
