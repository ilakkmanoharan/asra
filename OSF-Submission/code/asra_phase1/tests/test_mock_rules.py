from asra.viewer.mock_rules import START_GRID, apply_mock_action


def test_action1_cycles_top_left():
    nxt = apply_mock_action(START_GRID, "ACTION1")
    assert nxt[0][0] == 1
    assert nxt[1][1] == 1


def test_reset_from_start_is_noop():
    assert apply_mock_action(START_GRID, "RESET") == START_GRID
