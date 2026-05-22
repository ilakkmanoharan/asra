"""Persist action-test reports per state hash (Phase 1 action-effect memory)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from asra.agent.action_tester import build_action_test_report
from asra.utils.serialization import write_json


def observed_results_from_memory(
    state_hash: str,
    action_memory: dict[str, dict[str, list[dict[str, Any]]]],
) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for action, transitions in action_memory.get(state_hash, {}).items():
        if not transitions:
            continue
        last = transitions[-1]
        results[action] = {
            "next_state_hash": last["next_state"]["state_hash"],
            "changed_cells": last.get("diff", {}).get("num_changed_cells", 0),
            "terminal": last.get("terminal_state", False),
            "dead_end": last.get("metadata", {}).get("dead_end_score", 0.0) >= 0.8,
        }
    return results


def maybe_save_action_report(
    state: dict[str, Any],
    actions: list[str],
    action_memory: dict[str, dict[str, list[dict[str, Any]]]],
    reports_dir: Path,
    *,
    min_observed: int = 1,
) -> dict[str, Any] | None:
    state_hash = state.get("state_hash") or state["grid"]
    observed = observed_results_from_memory(state_hash, action_memory)
    if len(observed) < min_observed:
        return None
    report = build_action_test_report(state, actions, observed)
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"{state_hash}.json"
    write_json(path, report)
    return report
