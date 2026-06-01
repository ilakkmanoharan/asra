from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from asra.perception.arc_loader import ArcTask, load_arc_task, load_arc_tasks_from_dir
from asra.perception.objects import ObjectExtractor
from asra.perception.regions import RegionDetector
from asra.perception.rules import RuleCandidateGenerator
from asra.perception.schemas import ObjectScene, TransformDetection
from asra.perception.transforms import TransformationDetector


class BeforeAfterAnalyzer:
    """End-to-end Phase 2 runner for ARC demo pairs."""

    def __init__(self) -> None:
        self.extractor = ObjectExtractor()
        self.regions = RegionDetector()
        self.detector = TransformationDetector()
        self.rules = RuleCandidateGenerator()

    def scene_from_grid(self, grid: list[list[int]]) -> ObjectScene:
        scene = self.extractor.extract(grid)
        return self.regions.annotate(grid, scene)

    def analyze_pair(
        self,
        input_grid: list[list[int]],
        output_grid: list[list[int]],
        pair_id: str = "pair",
    ) -> dict[str, Any]:
        scene_in = self.scene_from_grid(input_grid)
        scene_out = self.scene_from_grid(output_grid)
        detection = self.detector.detect_scenes(scene_in, scene_out)
        return {
            "pair_id": pair_id,
            "input_scene": scene_in.to_dict(),
            "output_scene": scene_out.to_dict(),
            "transform": detection.to_dict(),
        }

    def analyze_task(self, task: ArcTask) -> dict[str, Any]:
        pair_reports: list[dict[str, Any]] = []
        demo_detections: list[TransformDetection] = []
        for pair in task.train_pairs:
            if pair.output_grid is None:
                continue
            pair_reports.append(self.analyze_pair(pair.input_grid, pair.output_grid, pair.pair_id))
            demo_detections.append(self.detector.detect_grids(pair.input_grid, pair.output_grid))

        rule_candidates = self.rules.generate(demo_detections)
        return {
            "task_id": task.task_id,
            "num_train_pairs": len(pair_reports),
            "pair_reports": pair_reports,
            "rule_candidates": [r.to_dict() for r in rule_candidates],
        }

    def analyze_directory(self, root: Path | str, output_dir: Path | str) -> list[Path]:
        root = Path(root)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        for task in load_arc_tasks_from_dir(root):
            report = self.analyze_task(task)
            out_path = output_dir / f"{task.task_id}.json"
            out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            written.append(out_path)
        return written


def analyze_grid_pair(
    input_grid: list[list[int]],
    output_grid: list[list[int]],
) -> dict[str, Any]:
    return BeforeAfterAnalyzer().analyze_pair(input_grid, output_grid)


def analyze_arc_task(task: ArcTask) -> dict[str, Any]:
    return BeforeAfterAnalyzer().analyze_task(task)


def run_phase2_batch(arc_root: Path | str, output_dir: Path | str) -> list[Path]:
    return BeforeAfterAnalyzer().analyze_directory(arc_root, output_dir)
