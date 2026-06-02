from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

from asra.causality.semantics_store import SemanticsStore


def iter_transitions_jsonl(input_dir: str | Path) -> Iterator[dict[str, Any]]:
    root = Path(input_dir)
    for path in sorted(root.rglob("*.jsonl")):
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)


def build_semantics_from_transitions(
    input_dir: str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    store = SemanticsStore()
    count = 0
    for transition in iter_transitions_jsonl(input_dir):
        store.ingest_transition(transition)
        count += 1
    paths = store.save(output_dir)
    signatures = store.summarizer.summarize_all()
    return {
        "transitions_processed": count,
        "signature_count": len(signatures),
        "output_paths": {k: str(v) for k, v in paths.items()},
        "games": sorted({s.game_id for s in signatures}),
    }


def eval_prediction_mae(input_dir: str | Path) -> dict[str, float]:
    """Hold-out style MAE: predict before observing each transition."""
    from asra.causality.transition_model import CausalTransitionModel

    model = CausalTransitionModel()
    errors: list[float] = []
    global_cells: list[float] = []
    for transition in iter_transitions_jsonl(input_dir):
        game_id = str(transition.get("game_id") or "unknown")
        state = transition.get("state") or {}
        state_hash = str(state.get("state_hash") or "")
        action = str((transition.get("action") or {}).get("name") or "")
        actual = float((transition.get("diff") or {}).get("num_changed_cells") or 0)
        global_cells.append(actual)
        pred = model.predict(game_id, state_hash, action)
        if pred.support_count > 0:
            errors.append(abs(pred.predicted_changed_cells - actual))
        model.observe_transition(transition)
    global_mean = sum(global_cells) / len(global_cells) if global_cells else 0.0
    mae = sum(errors) / len(errors) if errors else 0.0
    naive_mae = sum(abs(c - global_mean) for c in global_cells) / len(global_cells) if global_cells else 0.0
    return {
        "prediction_mae": mae,
        "naive_global_mean_mae": naive_mae,
        "evaluated_predictions": len(errors),
        "transitions": len(global_cells),
    }


def build_semantics_from_arc_exploration(data_dir: str | Path = "data/arc_exploration") -> dict[str, Any]:
    root = Path(data_dir)
    transitions_dir = root / "transitions"
    output_dir = root / "semantics"
    if not transitions_dir.is_dir():
        transitions_dir = Path("data/transitions")
        output_dir = Path("data/causality/arc/semantics")
    return build_semantics_from_transitions(transitions_dir, output_dir)
