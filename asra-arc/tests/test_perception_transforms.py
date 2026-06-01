from pathlib import Path

from asra.perception import BeforeAfterAnalyzer, TransformationDetector, load_arc_task
from asra.perception.schemas import TransformClass


def test_detect_translate():
    before = [
        [0, 0, 0, 0, 0],
        [0, 0, 2, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    after = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 2],
        [0, 0, 0, 0, 0],
    ]
    det = TransformationDetector().detect_grids(before, after)
    classes = {e.transform_class for e in det.events}
    assert TransformClass.TRANSLATE in classes or TransformClass.IDENTITY in classes
    assert any(e.object_id_before for e in det.events)


def test_detect_create_object():
    before = [[0, 0], [0, 0]]
    after = [[0, 2], [0, 0]]
    det = TransformationDetector().detect_grids(before, after)
    assert any(e.transform_class == TransformClass.CREATE for e in det.events)


def test_analyze_arc_micro_task():
    root = Path(__file__).parent / "fixtures" / "arc_micro" / "task_translate"
    task = load_arc_task(root)
    report = BeforeAfterAnalyzer().analyze_task(task)
    assert report["num_train_pairs"] == 1
    assert report["rule_candidates"]
    assert report["pair_reports"][0]["input_scene"]["objects"]
