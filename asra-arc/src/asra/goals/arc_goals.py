from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

from asra.goals.goals_store import GoalsStore
from asra.goals.win_condition_inference import WinConditionInference


def iter_transitions_jsonl(input_dir: str | Path) -> Iterator[dict[str, Any]]:
    root = Path(input_dir)
    for path in sorted(root.rglob("*.jsonl")):
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)


def build_goals_from_transitions(
    input_dir: str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    store = GoalsStore()
    count = 0
    by_episode: dict[str, list[dict[str, Any]]] = {}
    for transition in iter_transitions_jsonl(input_dir):
        store.ingest_transition(transition)
        eid = str(transition.get("episode_id") or "unknown")
        by_episode.setdefault(eid, []).append(transition)
        count += 1
    paths = store.save(output_dir)
    win_infer = WinConditionInference()
    hindsight: list[dict[str, Any]] = []
    for game_id, hyps in store.hypotheses.items():
        for eid, transitions in by_episode.items():
            if transitions and str(transitions[0].get("game_id")) == game_id:
                lead = win_infer.infer_from_episode_tail(list(hyps), transitions)
                if lead:
                    hindsight.append(
                        {"episode_id": eid, "leading_template": lead.template_id, "game_id": game_id}
                    )
    return {
        "transitions_processed": count,
        "games": list(store.hypotheses.keys()),
        "hypothesis_counts": {g: len(h) for g, h in store.hypotheses.items()},
        "output_paths": {k: str(v) for k, v in paths.items()},
        "win_hindsight_samples": hindsight[:20],
    }


def eval_goals_on_transitions(input_dir: str | Path) -> dict[str, float]:
    store = GoalsStore()
    progress_matches = 0
    progress_total = 0
    for transition in iter_transitions_jsonl(input_dir):
        before_lead = None
        game_id = str(transition.get("game_id") or "unknown")
        if game_id in store.hypotheses and store.hypotheses[game_id]:
            before_lead = store.hypotheses[game_id][0].template_id
        store.ingest_transition(transition)
        meta = transition.get("metadata") or {}
        goals = meta.get("goals") or {}
        reward = float(transition.get("reward") or 0)
        if reward > 0 or goals.get("leading_template_id"):
            progress_total += 1
            if goals.get("leading_template_id"):
                progress_matches += 1
    n_games = len(store.hypotheses)
    return {
        "games_with_hypotheses": float(n_games),
        "progress_events": float(len(store.progress_log)),
        "progress_correlation": progress_matches / progress_total if progress_total else 0.0,
        "avg_hypotheses_per_game": sum(len(h) for h in store.hypotheses.values()) / n_games if n_games else 0.0,
    }


def bootstrap_from_arc_tasks(arc_tasks_dir: str | Path) -> dict[str, str]:
    """Map ARC task ids to template family from output/input diff heuristics."""
    root = Path(arc_tasks_dir)
    priors: dict[str, str] = {}
    for path in sorted(root.rglob("*.json"))[:200]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        train = (data.get("train") or [{}])[0]
        inp = train.get("input")
        out = train.get("output")
        if not inp or not out:
            continue
        if len(inp) != len(out) or len(inp[0]) != len(out[0]):
            priors[path.stem] = "transform_to_goal"
        else:
            priors[path.stem] = "match_pattern"
    return priors
