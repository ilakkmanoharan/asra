import pytest

from asra.env.frame_parser import parse_frame


def test_parse_valid_grid():
    frame = parse_frame({"game_id": "g", "level_id": "l", "step_index": 2, "grid": [[0, 1], [2, 3]], "status": "NOT_FINISHED"})
    assert frame.height == 2
    assert frame.width == 2
    assert frame.metadata["source"] == "arc-agi-3"


def test_missing_grid():
    with pytest.raises(ValueError, match="grid"):
        parse_frame({"status": "NOT_FINISHED"})


def test_non_rectangular_grid():
    with pytest.raises(ValueError, match="rectangular"):
        parse_frame({"grid": [[0], [1, 2]], "status": "NOT_FINISHED"})


def test_out_of_range_color():
    with pytest.raises(ValueError, match="0 to 15"):
        parse_frame({"grid": [[16]], "status": "NOT_FINISHED"})


def test_invalid_status():
    with pytest.raises(ValueError, match="Invalid status"):
        parse_frame({"grid": [[0]], "status": "DONE"})
