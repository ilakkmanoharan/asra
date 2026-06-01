from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ArcPair:
    input_grid: list[list[int]]
    output_grid: list[list[int]] | None = None
    pair_id: str = "pair_0"


@dataclass
class ArcTask:
    task_id: str
    train_pairs: list[ArcPair] = field(default_factory=list)
    test_pairs: list[ArcPair] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        def _pair_dict(p: ArcPair) -> dict[str, Any]:
            d: dict[str, Any] = {"input": p.input_grid, "pair_id": p.pair_id}
            if p.output_grid is not None:
                d["output"] = p.output_grid
            return d

        return {
            "task_id": self.task_id,
            "train": [_pair_dict(p) for p in self.train_pairs],
            "test": [_pair_dict(p) for p in self.test_pairs],
        }


def _parse_grid(raw: Any) -> list[list[int]]:
    if not isinstance(raw, list):
        raise ValueError("Grid must be a list of rows")
    return [[int(c) for c in row] for row in raw]


def load_arc_task(path: Path | str) -> ArcTask:
    path = Path(path)
    if path.is_dir():
        json_files = sorted(path.glob("*.json"))
        if not json_files:
            raise FileNotFoundError(f"No JSON in {path}")
        data = json.loads(json_files[0].read_text(encoding="utf-8"))
        task_id = path.name
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
        task_id = path.stem

    train_pairs: list[ArcPair] = []
    for i, pair in enumerate(data.get("train", [])):
        train_pairs.append(
            ArcPair(
                input_grid=_parse_grid(pair["input"]),
                output_grid=_parse_grid(pair["output"]) if "output" in pair else None,
                pair_id=f"train_{i}",
            )
        )
    test_pairs: list[ArcPair] = []
    for i, pair in enumerate(data.get("test", [])):
        test_pairs.append(
            ArcPair(
                input_grid=_parse_grid(pair["input"]),
                output_grid=_parse_grid(pair["output"]) if "output" in pair else None,
                pair_id=f"test_{i}",
            )
        )
    return ArcTask(task_id=task_id, train_pairs=train_pairs, test_pairs=test_pairs)


def load_arc_tasks_from_dir(root: Path | str) -> list[ArcTask]:
    root = Path(root)
    tasks: list[ArcTask] = []
    for entry in sorted(root.iterdir()):
        if entry.is_dir():
            try:
                tasks.append(load_arc_task(entry))
            except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
                continue
        elif entry.suffix == ".json":
            try:
                tasks.append(load_arc_task(entry))
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
    return tasks
