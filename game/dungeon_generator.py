from __future__ import annotations

from typing import List, Tuple, Optional
import random

from game.constants import (
    MAP_WIDTH, MAP_HEIGHT,
    MIN_ROOM_SIZE, MAX_ROOM_SIZE, MAX_ROOMS,
    MAX_MONSTERS_PER_ROOM
)


class Tile:
    def __init__(self, blocked: bool, block_sight: Optional[bool] = None):
        self.blocked = blocked
        self.block_sight = block_sight if block_sight is not None else blocked
        self.explored = False


class Rect:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return center_x, center_y

    def intersect(self, other: Rect) -> bool:
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class DungeonGenerator:
    def __init__(self, width: int = MAP_WIDTH, height: int = MAP_HEIGHT):
        self.width = width
        self.height = height
        self.map: List[List[Tile]] = []
        self.rooms: List[Rect] = []
        self.start_pos: Tuple[int, int] = (0, 0)
        self.stairs_pos: Tuple[int, int] = (0, 0)

    def generate(self, floor_level: int = 1) -> None:
        self.map = [[Tile(True) for _ in range(self.height)] for _ in range(self.width)]
        self.rooms = []

        self._generate_rooms_bsp(floor_level)

        self.start_pos = self.rooms[0].center()
        self.stairs_pos = self.rooms[-1].center()

        self._place_stairs()

    def _create_room(self, room: Rect) -> None:
        for x in range(room.x1, room.x2):
            for y in range(room.y1, room.y2):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.map[x][y].blocked = False
                    self.map[x][y].block_sight = False

    def _create_h_tunnel(self, x1: int, x2: int, y: int) -> None:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.map[x][y].blocked = False
                self.map[x][y].block_sight = False

    def _create_v_tunnel(self, y1: int, y2: int, x: int) -> None:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.map[x][y].blocked = False
                self.map[x][y].block_sight = False

    def _generate_rooms_bsp(self, floor_level: int) -> None:
        class BSPNode:
            def __init__(self, x: int, y: int, w: int, h: int):
                self.x = x
                self.y = y
                self.w = w
                self.h = h
                self.left: Optional[BSPNode] = None
                self.right: Optional[BSPNode] = None
                self.room: Optional[Rect] = None

            def split(self, depth: int = 0) -> None:
                if depth > 8:
                    return

                min_size = MIN_ROOM_SIZE

                if self.w < min_size * 2 and self.h < min_size * 2:
                    return

                horizontal = self.w < self.h
                if self.w > self.h * 1.5:
                    horizontal = False
                elif self.h > self.w * 1.5:
                    horizontal = True

                if horizontal:
                    if self.h < min_size * 2:
                        return
                    split_pos = random.randint(min_size, self.h - min_size)
                    self.left = BSPNode(self.x, self.y, self.w, split_pos)
                    self.right = BSPNode(self.x, self.y + split_pos, self.w, self.h - split_pos)
                else:
                    if self.w < min_size * 2:
                        return
                    split_pos = random.randint(min_size, self.w - min_size)
                    self.left = BSPNode(self.x, self.y, split_pos, self.h)
                    self.right = BSPNode(self.x + split_pos, self.y, self.w - split_pos, self.h)

                self.left.split(depth + 1)
                self.right.split(depth + 1)

            def create_room(self, generator: DungeonGenerator) -> Optional[Rect]:
                if self.left and self.right:
                    left_room = self.left.create_room(generator)
                    right_room = self.right.create_room(generator)
                    if left_room and right_room:
                        generator._connect_rooms(left_room, right_room)
                    return left_room or right_room
                else:
                    room_w = random.randint(MIN_ROOM_SIZE, min(self.w, MAX_ROOM_SIZE))
                    room_h = random.randint(MIN_ROOM_SIZE, min(self.h, MAX_ROOM_SIZE))
                    room_x = self.x + random.randint(0, self.w - room_w)
                    room_y = self.y + random.randint(0, self.h - room_h)

                    room = Rect(room_x, room_y, room_w, room_h)
                    if len(generator.rooms) < MAX_ROOMS:
                        generator._create_room(room)
                        generator.rooms.append(room)
                        self.room = room
                        return room
                return None

        root = BSPNode(1, 1, self.width - 2, self.height - 2)
        root.split()
        root.create_room(self)

        if not self.rooms:
            self._create_room(Rect(1, 1, 8, 6))
            self.rooms.append(Rect(1, 1, 8, 6))

    def _connect_rooms(self, room1: Rect, room2: Rect) -> None:
        x1, y1 = room1.center()
        x2, y2 = room2.center()

        if random.random() < 0.5:
            self._create_h_tunnel(x1, x2, y1)
            self._create_v_tunnel(y1, y2, x2)
        else:
            self._create_v_tunnel(y1, y2, x1)
            self._create_h_tunnel(x1, x2, y2)

    def _place_stairs(self) -> None:
        if self.stairs_pos[0] < self.width and self.stairs_pos[1] < self.height:
            pass

    def is_blocked(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return self.map[x][y].blocked

    def get_room_centers(self) -> List[Tuple[int, int]]:
        return [room.center() for room in self.rooms]
