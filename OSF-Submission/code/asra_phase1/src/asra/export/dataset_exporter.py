from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from asra.analysis.episode_summary import summarize_episode
from asra.memory.state_graph import build_graph_from_transition_dir
from asra.utils.serialization import read_jsonl, write_json


def export_dataset(input_dir: str | Path = "data/transitions", output_dir: str | Path = "data/exports") -> dict[str, str]:
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for path in sorted(input_dir.glob("*.jsonl")):
        transitions = read_jsonl(path)
        rows.extend(_flatten_transition(row) for row in transitions)
        summaries.append(summarize_episode(path.stem, transitions))

    jsonl_path = output_dir / "asra_v0_1_transitions.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    parquet_path = output_dir / "asra_v0_1_transitions.parquet"
    try:
        import pandas as pd
        pd.DataFrame(rows).to_parquet(parquet_path, index=False)
    except Exception as exc:
        raise RuntimeError("Parquet export requires pandas and pyarrow") from exc

    summary_path = output_dir / "asra_v0_1_episode_summary.csv"
    fieldnames = ["episode_id", "game_id", "level_id", "num_steps", "unique_states", "num_cycles", "num_dead_ends", "final_status", "total_reward", "actions_used"]
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for summary in summaries:
            row = dict(summary)
            row["actions_used"] = json.dumps(row["actions_used"], sort_keys=True)
            writer.writerow(row)

    graph_path = output_dir / "asra_v0_1_state_graph.json"
    graph = build_graph_from_transition_dir(input_dir)
    write_json(graph_path, graph.to_dict())
    return {"jsonl": str(jsonl_path), "parquet": str(parquet_path), "summary_csv": str(summary_path), "state_graph": str(graph_path)}


def _flatten_transition(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "episode_id": row["episode_id"],
        "game_id": row["game_id"],
        "level_id": row["level_id"],
        "step_index": row["step_index"],
        "state": row["state"],
        "action": row["action"],
        "next_state": row["next_state"],
        "reward": row["reward"],
        "terminal_state": row["terminal_state"],
        "metadata": row.get("metadata", {}),
        "state_hash": row["state"]["state_hash"],
        "next_state_hash": row["next_state"]["state_hash"],
        "diff": row.get("diff", {}),
        "policy_name": row.get("metadata", {}).get("policy", "simple_exploration"),
        "agent_version": row.get("metadata", {}).get("agent_version", "asra-v0.1"),
    }
