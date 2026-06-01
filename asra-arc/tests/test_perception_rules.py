from asra.perception.rules import RuleCandidateGenerator
from asra.perception.schemas import TransformClass, TransformDetection, TransformEvent


def _det(*event_types: TransformClass) -> TransformDetection:
    events = [
        TransformEvent(transform_class=t, object_id_before="a", object_id_after="b")
        for t in event_types
    ]
    summary = event_types[0].value if len(event_types) == 1 else "mixed"
    return TransformDetection(events=events, summary=summary)


def test_unanimous_common_rule_confidence_one():
    dets = [_det(TransformClass.ROTATE), _det(TransformClass.ROTATE)]
    rules = RuleCandidateGenerator().generate(dets)
    assert rules[0].pattern.startswith("APPLY_ROTATE")
    assert rules[0].confidence == 1.0
    assert rules[0].rule_scope == "global"


def test_mixed_demos_emit_branched_and_per_demo_rules():
    dets = [
        _det(TransformClass.IDENTITY),
        _det(TransformClass.CREATE, TransformClass.DELETE),
        _det(TransformClass.ROTATE),
    ]
    rules = RuleCandidateGenerator().generate(dets)
    assert rules[0].pattern == "BRANCHED_PER_DEMO"
    assert rules[0].rule_scope == "branched"
    per_demo = [r for r in rules if r.rule_scope == "per_demo"]
    assert len(per_demo) == 3
    assert per_demo[0].demo_index == 0
    assert "IDENTITY" in per_demo[0].pattern
    assert per_demo[1].demo_index == 1
    assert per_demo[1].confidence == 1.0


def test_exception_task_reports_branched_top_rule():
    from pathlib import Path

    import json

    from asra.perception.analyzer import BeforeAfterAnalyzer
    from asra.perception.arc_loader import load_arc_task

    arc_root = Path("data/arc/original/_repo/training")
    if not arc_root.is_dir():
        return
    task = load_arc_task(arc_root / "22eb0ac0.json")
    report = BeforeAfterAnalyzer().analyze_task(task)
    top = report["rule_candidates"][0]
    assert top["pattern"] == "BRANCHED_PER_DEMO"
    per_demo = [r for r in report["rule_candidates"] if r.get("rule_scope") == "per_demo"]
    assert len(per_demo) == report["num_train_pairs"]
