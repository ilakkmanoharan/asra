from asra.perception.objects import ObjectExtractor
from asra.perception.schemas import TransformClass
from asra.perception.shapes import ShapeMatcher, shape_similarity


def test_shape_similarity_identical():
    grid = [[0, 2, 0], [0, 0, 0], [0, 0, 0]]
    scene = ObjectExtractor(background_color=0).extract(grid)
    obj = scene.objects[0]
    assert shape_similarity(obj, obj) == 1.0


def test_shape_similarity_rotated_square():
    a = ObjectExtractor(background_color=0).extract(
        [[2, 2], [2, 2]]
    ).objects[0]
    b = ObjectExtractor(background_color=0).extract(
        [[2, 2], [2, 2]]
    ).objects[0]
    m = ShapeMatcher().match(a, b)
    assert m.similarity >= 0.99
    assert m.transform_class in (TransformClass.IDENTITY, TransformClass.ROTATE)


def test_translate_objects_different_positions():
    before = [[0, 0, 0, 0], [0, 2, 0, 0], [0, 0, 0, 0]]
    after = [[0, 0, 0, 0], [0, 0, 0, 2], [0, 0, 0, 0]]
    obj_a = ObjectExtractor(background_color=0).extract(before).objects[0]
    obj_b = ObjectExtractor(background_color=0).extract(after).objects[0]
    m = ShapeMatcher().match(obj_a, obj_b)
    assert m.similarity >= 0.85
