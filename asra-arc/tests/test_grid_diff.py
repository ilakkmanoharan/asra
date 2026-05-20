from asra.analysis.grid_diff import diff_grid


def test_no_change():
    diff = diff_grid([[1]], [[1]])
    assert diff["num_changed_cells"] == 0
    assert diff["unchanged_ratio"] == 1.0


def test_single_cell_change():
    diff = diff_grid([[0, 0]], [[0, 3]])
    assert diff["changed_cells"] == [{"x": 1, "y": 0, "from": 0, "to": 3}]
    assert diff["change_ratio"] == 0.5


def test_multi_cell_change():
    diff = diff_grid([[0, 1], [2, 3]], [[1, 1], [2, 4]])
    assert diff["num_changed_cells"] == 2


def test_added_removed_colors():
    diff = diff_grid([[1, 1]], [[1, 2]])
    assert diff["added_colors"] == [2]
    assert diff["removed_colors"] == []
