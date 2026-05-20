from __future__ import annotations

from pathlib import Path

from asra.utils.serialization import read_jsonl


def render_grid(grid: list[list[int]]) -> str:
    return "\n".join(" ".join(f"{cell:02d}" for cell in row) for row in grid)


def replay_episode(episode_id: str, data_dir: str | Path = "data") -> str:
    path = Path(data_dir) / "transitions" / f"{episode_id}.jsonl"
    transitions = read_jsonl(path)
    parts = [f"Episode ID: {episode_id}"]
    for row in transitions:
        parts.extend([
            f"Step: {row['step_index']} | Action: {row['action']['name']} | Status: {row['next_state']['status']} | Reward: {row['reward']}",
            "Grid before:",
            render_grid(row["state"]["grid"]),
            "Grid after:",
            render_grid(row["next_state"]["grid"]),
            f"Changed cells: {row.get('diff', {}).get('num_changed_cells', 0)}",
            "",
        ])
    output = "\n".join(parts)
    print(output)
    return output
