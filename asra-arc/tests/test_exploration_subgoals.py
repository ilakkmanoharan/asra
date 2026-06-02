from asra.exploration.subgoals import detect_minigrid_milestones, parse_babyai_mission


def test_parse_babyai_goto_mission() -> None:
    subgoals = parse_babyai_mission("go to the red ball")
    assert len(subgoals) >= 1
    assert subgoals[0].subgoal_id == "goto_target"
    assert subgoals[0].status == "active"
    assert "ball" in subgoals[0].description


def test_parse_babyai_pickup_mission() -> None:
    subgoals = parse_babyai_mission("pick up the grey key")
    ids = [s.subgoal_id for s in subgoals]
    assert "pickup" in ids


def test_minigrid_milestones() -> None:
    flags = detect_minigrid_milestones(carrying=True, door_open=False, at_goal=False)
    assert flags["has_key_or_carrying"] is True
    assert flags["at_goal"] is False
