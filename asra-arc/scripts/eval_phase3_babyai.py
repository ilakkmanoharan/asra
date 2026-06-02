#!/usr/bin/env python3
"""Evaluate BabyAI subgoal detection accuracy vs replay oracle."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from asra.exploration.babyai_runner import run_babyai_batch
from asra.exploration.subgoals import SubgoalDetector
from asra.utils.serialization import read_jsonl


def oracle_from_transitions(env_id: str, seed: int, transitions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    import gymnasium as gym
    import minigrid  # noqa: F401

    env = gym.make(env_id)
    env.reset(seed=seed)
    mission = str(env.unwrapped.mission)
    detector = SubgoalDetector.from_mission(mission)
    events: list[dict[str, Any]] = []
    for row in transitions:
        action_name = row["action"]["name"]
        action_idx = int(action_name.replace("ACTION", "")) - 1
        env.step(action_idx)
        step = row["step_index"]
        before = {sg.subgoal_id for sg in detector.subgoals if sg.status == "completed"}
        detector.update(env, step, terminated=row.get("next_state", {}).get("status") == "WIN", reward=float(row.get("reward", 0)))
        for sg in detector.subgoals:
            if sg.subgoal_id not in before and sg.status == "completed":
                events.append({"step": step, "subgoal_id": sg.subgoal_id})
    env.close()
    return events


def logged_completion_steps(transition_path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for row in read_jsonl(transition_path):
        meta = row.get("metadata", {}).get("exploration", {})
        if meta.get("subgoal_complete") and meta.get("subgoal_complete_id"):
            events.append({"step": row["step_index"], "subgoal_id": meta["subgoal_complete_id"]})
    return events


def evaluate_episode(env_id: str, seed: int, max_steps: int, data_dir: Path) -> dict[str, Any]:
    results = run_babyai_batch(env_id=env_id, episodes=1, max_steps=max_steps, data_dir=str(data_dir), seed=seed)
    result = results[0]
    transitions = list(read_jsonl(Path(result.transition_path)))
    logged = logged_completion_steps(Path(result.transition_path))
    oracle = oracle_from_transitions(env_id, seed, transitions)
    matched = sum(1 for lg in logged if any(o["subgoal_id"] == lg["subgoal_id"] for o in oracle))
    accuracy = matched / max(len(oracle), 1) if oracle else (1.0 if not logged else 0.0)
    return {
        "episode_id": result.episode_id,
        "mission": result.mission,
        "success": result.success,
        "steps": result.steps,
        "logged_events": len(logged),
        "oracle_events": len(oracle),
        "matched_events": matched,
        "subgoal_accuracy": round(accuracy, 4),
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Evaluate Phase 3 BabyAI subgoal metrics")
    p.add_argument("--env", default="BabyAI-GoToRedBallGrey-v0")
    p.add_argument("--episodes", type=int, default=5)
    p.add_argument("--max-steps", type=int, default=200)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--output-json", default="data/analysis/phase3/babyai_summary.json")
    p.add_argument("--output-csv", default="data/analysis/phase3/babyai_subgoals.csv")
    args = p.parse_args()

    rows: list[dict[str, Any]] = []
    for i in range(args.episodes):
        rows.append(
            evaluate_episode(
                args.env,
                seed=args.seed + i,
                max_steps=args.max_steps,
                data_dir=Path("data/babyai") / f"eval_{args.seed + i}",
            )
        )

    mean_accuracy = sum(r["subgoal_accuracy"] for r in rows) / len(rows) if rows else 0.0
    summary = {
        "env_id": args.env,
        "episodes": args.episodes,
        "mean_subgoal_accuracy": round(mean_accuracy, 4),
        "success_rate": round(sum(1 for r in rows if r["success"]) / len(rows), 4) if rows else 0.0,
        "episodes_detail": rows,
    }

    out_json = Path(args.output_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    out_csv = Path(args.output_csv)
    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["episode_id", "mission", "success", "steps", "subgoal_accuracy", "logged_events", "oracle_events"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in writer.fieldnames})

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
