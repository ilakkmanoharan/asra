#!/usr/bin/env python3
"""Inspect Phase 2 tasks where cross-demo rule confidence < 1.0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def inspect_report(report: dict[str, Any]) -> dict[str, Any]:
    rules = report.get("rule_candidates") or []
    top = rules[0] if rules else {}
    per_pair_summaries: list[dict[str, Any]] = []
    for pair in report.get("pair_reports", []):
        transform = pair.get("transform", {})
        per_pair_summaries.append(
            {
                "pair_id": pair.get("pair_id"),
                "summary": transform.get("summary"),
                "num_events": len(transform.get("events", [])),
                "num_input_objects": len(pair.get("input_scene", {}).get("objects", [])),
                "num_output_objects": len(pair.get("output_scene", {}).get("objects", [])),
                "event_types": sorted({e.get("transform_class") for e in transform.get("events", [])}),
            }
        )
    unique_summaries = {p["summary"] for p in per_pair_summaries}
    return {
        "task_id": report.get("task_id"),
        "num_train_pairs": report.get("num_train_pairs"),
        "top_rule_pattern": top.get("pattern"),
        "top_rule_confidence": top.get("confidence"),
        "top_rule_support": top.get("support"),
        "all_rules": [(r.get("pattern"), r.get("confidence"), r.get("support")) for r in rules[:5]],
        "per_pair": per_pair_summaries,
        "inconsistent_demo_summaries": len(unique_summaries) > 1,
        "unique_transform_summaries": sorted(unique_summaries),
        "likely_cause": _infer_cause(per_pair_summaries, unique_summaries),
    }


def _infer_cause(per_pair: list[dict[str, Any]], unique_summaries: set[str]) -> str:
    if len(unique_summaries) <= 1:
        return "consistent"
    event_sets = [tuple(p["event_types"]) for p in per_pair]
    if len(set(event_sets)) > 1:
        return "mixed_transform_types_across_demos"
    obj_counts = [(p["num_input_objects"], p["num_output_objects"]) for p in per_pair]
    if len(set(obj_counts)) > 1:
        return "varying_object_counts_across_demos"
    return "differing_transform_summary_same_event_types"


def write_markdown(rows: list[dict[str, Any]], out_path: Path, label: str) -> None:
    lines = [
        f"# Phase 2 exception tasks — {label}",
        "",
        f"Tasks where top rule `confidence < 1.0` (inconsistent cross-demo pattern): **{len(rows)}**",
        "",
    ]
    for row in rows:
        lines.append(f"## `{row['task_id']}`")
        lines.append("")
        lines.append(f"- **Likely cause:** {row['likely_cause']}")
        lines.append(f"- **Top rule:** `{row['top_rule_pattern']}` (confidence={row['top_rule_confidence']}, support={row['top_rule_support']})")
        lines.append(f"- **Demo transform summaries:** {', '.join(row['unique_transform_summaries'])}")
        lines.append("")
        lines.append("| pair | input objs | output objs | events | summary |")
        lines.append("|------|------------|-------------|--------|---------|")
        for p in row["per_pair"]:
            lines.append(
                f"| {p['pair_id']} | {p['num_input_objects']} | {p['num_output_objects']} | "
                f"{p['num_events']} | {p['summary']} |"
            )
        lines.append("")
        if row["all_rules"]:
            lines.append("**Rule candidates:**")
            for pat, conf, sup in row["all_rules"]:
                lines.append(f"- `{pat}` — confidence={conf}, support={sup}")
            lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--report-dir", required=True)
    p.add_argument("--summary-json", help="Optional summary JSON with exception_task_ids")
    p.add_argument("--output-json", default="data/analysis/phase2/exceptions_detail.json")
    p.add_argument("--output-md", default="data/analysis/phase2/EXCEPTIONS_REPORT.md")
    p.add_argument("--label", default="combined")
    args = p.parse_args()

    report_dir = Path(args.report_dir)
    exception_ids: set[str] = set()
    if args.summary_json:
        summary = json.loads(Path(args.summary_json).read_text(encoding="utf-8"))
        exception_ids = set(summary.get("exception_task_ids", []))

    rows: list[dict[str, Any]] = []
    for path in sorted(report_dir.glob("*.json")):
        report = _load_report(path)
        rules = report.get("rule_candidates") or []
        is_exception = path.stem in exception_ids or (
            rules and rules[0].get("confidence", 1.0) < 1.0
        )
        if is_exception:
            rows.append(inspect_report(report))

    out_json = Path(args.output_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    write_markdown(rows, Path(args.output_md), args.label)
    print(f"Exceptions: {len(rows)}")
    print(f"Wrote {out_json}")
    print(f"Wrote {args.output_md}")


if __name__ == "__main__":
    main()
