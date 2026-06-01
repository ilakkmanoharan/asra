from __future__ import annotations

from asra.perception.objects import _bbox, _dominant_background
from asra.perception.schemas import ObjectScene, Region, RegionType


class RegionDetector:
    """Detect background and content bounding regions on a grid."""

    def annotate(self, grid: list[list[int]], scene: ObjectScene) -> ObjectScene:
        if not grid or not grid[0]:
            return scene
        h, w = len(grid), len(grid[0])
        bg = scene.background_color
        bg_pixels = [(y, x) for y in range(h) for x in range(w) if grid[y][x] == bg]
        regions: list[Region] = [
            Region(
                region_id="reg_background",
                region_type=RegionType.BACKGROUND,
                color=bg,
                bbox=(0, 0, h - 1, w - 1),
                area=len(bg_pixels),
            )
        ]
        if scene.objects:
            all_pixels = [p for obj in scene.objects for p in obj.pixels]
            regions.append(
                Region(
                    region_id="reg_content_bbox",
                    region_type=RegionType.CONTENT_BBOX,
                    color=None,
                    bbox=_bbox(all_pixels),
                    area=len(all_pixels),
                )
            )
        if self._has_uniform_border(grid):
            regions.append(
                Region(
                    region_id="reg_frame",
                    region_type=RegionType.FRAME,
                    color=grid[0][0],
                    bbox=(0, 0, h - 1, w - 1),
                    area=2 * (h + w) - 4,
                )
            )
        scene.regions = regions
        return scene

    @staticmethod
    def _has_uniform_border(grid: list[list[int]]) -> bool:
        h, w = len(grid), len(grid[0])
        if h < 3 or w < 3:
            return False
        top = grid[0][0]
        if not all(grid[0][x] == top for x in range(w)):
            return False
        if not all(grid[h - 1][x] == top for x in range(w)):
            return False
        if not all(grid[y][0] == top for y in range(h)):
            return False
        if not all(grid[y][w - 1] == top for y in range(h)):
            return False
        return True

    def detect(self, grid: list[list[int]]) -> list[Region]:
        bg = _dominant_background(grid)
        scene = ObjectScene(grid_shape=(len(grid), len(grid[0]) if grid else 0), background_color=bg)
        return self.annotate(grid, scene).regions
