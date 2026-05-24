from __future__ import annotations

from typing import List
import math

from game.constants import TORCH_RADIUS


class FOVCalculator:
    def __init__(self, radius: int = TORCH_RADIUS):
        self.radius = radius

    def calculate(self, map_data, player_x: int, player_y: int) -> List[List[bool]]:
        width = len(map_data)
        height = len(map_data[0]) if width > 0 else 0

        visible = [[False for _ in range(height)] for _ in range(width)]

        self._set_visible(visible, player_x, player_y)

        for angle in range(0, 360, 1):
            rad = math.radians(angle)
            dx = math.cos(rad)
            dy = math.sin(rad)
            self._cast_ray(map_data, visible, player_x, player_y, dx, dy)

        return visible

    def _cast_ray(self, map_data, visible, start_x: int, start_y: int,
                  dx: float, dy: float) -> None:
        x = float(start_x) + 0.5
        y = float(start_y) + 0.5

        for _ in range(self.radius):
            ix = int(x)
            iy = int(y)

            if ix < 0 or ix >= len(map_data) or iy < 0 or iy >= len(map_data[0]):
                break

            self._set_visible(visible, ix, iy)

            if map_data[ix][iy].block_sight:
                break

            x += dx
            y += dy

    def _set_visible(self, visible, x: int, y: int) -> None:
        if 0 <= x < len(visible) and 0 <= y < len(visible[0]):
            visible[x][y] = True
