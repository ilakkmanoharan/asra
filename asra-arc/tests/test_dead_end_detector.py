from asra.agent.dead_end_detector import detect_dead_end


def test_detects_no_change_state():
    report = detect_dead_end("s", [{"next_state_hash": "s", "changed_cells": 0} for _ in range(8)])
    assert report["dead_end_score"] >= 0.8
    assert report["recommended_action"] == "RESET"


def test_detects_cycle():
    report = detect_dead_end("s", recent_states=["a", "b", "a", "a"])
    assert "cycle_detected" in report["reasons"]


def test_detects_game_over():
    report = detect_dead_end("s", status="GAME_OVER")
    assert report["dead_end_score"] == 1.0
