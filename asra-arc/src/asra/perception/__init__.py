"""ASRA Phase 2 — abstraction and symbolic perception (object-centric grids)."""

from asra.perception.analyzer import (
    BeforeAfterAnalyzer,
    analyze_arc_task,
    analyze_grid_pair,
    run_phase2_batch,
)
from asra.perception.arc_loader import ArcTask, load_arc_task, load_arc_tasks_from_dir
from asra.perception.objects import ObjectExtractor
from asra.perception.rules import RuleCandidate, RuleCandidateGenerator
from asra.perception.schemas import (
    GridObject,
    MatchResult,
    ObjectScene,
    Region,
    TransformClass,
    TransformDetection,
    TransformEvent,
)
from asra.perception.transforms import TransformationDetector

__all__ = [
    "ArcTask",
    "BeforeAfterAnalyzer",
    "GridObject",
    "MatchResult",
    "ObjectExtractor",
    "ObjectScene",
    "Region",
    "RuleCandidate",
    "RuleCandidateGenerator",
    "TransformClass",
    "TransformDetection",
    "TransformEvent",
    "TransformationDetector",
    "analyze_arc_task",
    "analyze_grid_pair",
    "run_phase2_batch",
    "load_arc_task",
    "load_arc_tasks_from_dir",
]
