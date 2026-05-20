from __future__ import annotations

from typing import Any

from asra.utils.hashing import hash_state


def classify_effect(changed_cells: int, total_cells: int, terminal: bool, repeated_state: bool, dead_end: bool = False) -> str:
    if terminal:
        return "terminal_transition"
    if dead_end:
        return "dead_end"
    if repeated_state:
        return "repeated_state"
    if changed_cells == 0:
        return "no_change"
    ratio = changed_cells / total_cells if total_cells else 0.0
    return "small_change" if ratio <= 0.25 else "large_change"


def test_actions_from_state(state: dict[str, Any], actions: list[str], observed_results: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    state_hash = state.get("state_hash") or hash_state(state["grid"])
    total_cells = state.get("height", len(state["grid"])) * state.get("width", len(state["grid"][0]))
    reports = []
    for action in actions:
        result = (observed_results or {}).get(action)
        if result is None:
            reports.append({"action": action, "next_state_hash": None, "changed_cells": None, "terminal": None, "effect_type": "untested"})
            continue
        next_hash = result.get("next_state_hash") or result.get("next_state", {}).get("state_hash")
        changed = result.get("changed_cells", result.get("diff", {}).get("num_changed_cells", 0))
        terminal = bool(result.get("terminal", result.get("terminal_state", False)))
        reports.append({
            "action": action,
            "next_state_hash": next_hash,
            "changed_cells": changed,
            "terminal": terminal,
            "effect_type": classify_effect(changed, total_cells, terminal, next_hash == state_hash, bool(result.get("dead_end", False))),
        })
    return {"state_hash": state_hash, "tested_actions": reports}
