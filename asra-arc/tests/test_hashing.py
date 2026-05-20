from asra.utils.hashing import hash_state


def test_same_grid_same_hash():
    assert hash_state([[1, 2]]) == hash_state([[1, 2]])


def test_different_grid_different_hash():
    assert hash_state([[1, 2]]) != hash_state([[2, 1]])


def test_shape_affects_hash():
    assert hash_state([[1, 2]]) != hash_state([[1], [2]])


def test_timestamp_not_in_hash():
    assert hash_state([[1]], {"timestamp": "a"}) == hash_state([[1]], {"timestamp": "b"})
