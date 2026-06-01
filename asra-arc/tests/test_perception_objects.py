from asra.perception import ObjectExtractor


def test_extract_single_object():
    grid = [
        [0, 0, 0],
        [0, 2, 0],
        [0, 0, 0],
    ]
    scene = ObjectExtractor().extract(grid)
    assert len(scene.objects) == 1
    assert scene.objects[0].color == 2
    assert scene.objects[0].area == 1


def test_extract_multiple_objects():
    grid = [
        [1, 0, 1],
        [0, 0, 0],
        [1, 0, 0],
    ]
    scene = ObjectExtractor(background_color=0).extract(grid)
    assert len(scene.objects) == 3
    assert all(o.color == 1 for o in scene.objects)


def test_extract_l_shape_connected():
    grid = [
        [0, 2, 0],
        [0, 2, 0],
        [0, 2, 2],
    ]
    scene = ObjectExtractor(background_color=0).extract(grid)
    assert len(scene.objects) == 1
    assert scene.objects[0].area == 4
