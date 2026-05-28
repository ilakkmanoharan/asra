from asra.agent.action_tester import build_action_test_report, classify_effect


def test_classify_effect_types():
    assert classify_effect(0, 9, False, False) == "no_change"
    assert classify_effect(2, 9, False, False) == "small_change"
    assert classify_effect(8, 9, False, False) == "large_change"
    assert classify_effect(1, 9, True, False) == "terminal_transition"


def test_action_test_report():
    state = {"grid": [[0, 1], [2, 3]], "height": 2, "width": 2, "state_hash": "abc"}
    observed = {
        "ACTION1": {"next_state_hash": "def", "changed_cells": 1, "terminal": False},
        "ACTION2": {"next_state_hash": "abc", "changed_cells": 0, "terminal": False},
    }
    report = build_action_test_report(state, ["ACTION1", "ACTION2", "ACTION3"], observed)
    assert report["state_hash"] == "abc"
    by_action = {row["action"]: row for row in report["tested_actions"]}
    assert by_action["ACTION1"]["effect_type"] == "small_change"
    assert by_action["ACTION2"]["effect_type"] == "repeated_state"
    assert by_action["ACTION3"]["effect_type"] == "untested"
