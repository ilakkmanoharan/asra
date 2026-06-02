from asra.exploration.subgoals import SubgoalDetector, parse_babyai_mission


def test_subgoal_detector_goto_mission() -> None:
    detector = SubgoalDetector.from_mission("go to the red ball")
    assert detector.active_subgoal() is not None
    assert detector.active_subgoal().subgoal_id == "goto_target"


def test_subgoal_detector_doorkey_chain() -> None:
    detector = SubgoalDetector.for_doorkey()
    ids = [sg.subgoal_id for sg in detector.subgoals]
    assert ids == ["has_key", "door_open", "at_goal"]


class _FakeCarrying:
    type = "key"


class _FakeEnv:
    def __init__(self) -> None:
        self.unwrapped = self
        self.carrying = _FakeCarrying()
        self.front_pos = (0, 0)
        self.instrs = None
        self.grid = None


def test_subgoal_detector_key_complete() -> None:
    detector = SubgoalDetector.for_doorkey()
    detector.update(_FakeEnv(), step=5)
    assert detector.subgoals[0].status == "completed"
    assert detector.subgoals[1].status == "active"
