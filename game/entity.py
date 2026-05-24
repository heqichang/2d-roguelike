from __future__ import annotations

from typing import Optional, List, Tuple

from game.constants import TORCH_RADIUS


class Entity:
    def __init__(self, x: int, y: int, char: str, color: Tuple[int, int, int],
                 name: str, blocks: bool = True):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy


class Fighter(Entity):
    def __init__(self, x: int, y: int, char: str, color: Tuple[int, int, int],
                 name: str, hp: int, atk: int, defense: int, exp: int = 0,
                 blocks: bool = True):
        super().__init__(x, y, char, color, name, blocks)
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.exp = exp

    def take_damage(self, damage: int) -> int:
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        return actual_damage

    def is_dead(self) -> bool:
        return self.hp <= 0

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + amount)


class Player(Fighter):
    def __init__(self, x: int, y: int):
        super().__init__(
            x=x, y=y,
            char='@',
            color=(255, 255, 255),
            name='玩家',
            hp=30,
            atk=5,
            defense=2,
            exp=0
        )
        self.level = 1
        self.floor = 1
        self.fov_radius = TORCH_RADIUS
        self.visible: List[List[bool]] = []
        self.explored: List[List[bool]] = []

    def level_up(self) -> None:
        self.level += 1
        self.max_hp += 10
        self.hp = self.max_hp
        self.atk += 2
        self.defense += 1

    def gain_exp(self, amount: int) -> None:
        self.exp += amount
        exp_needed = self.level * 100
        while self.exp >= exp_needed:
            self.exp -= exp_needed
            self.level_up()
            exp_needed = self.level * 100


class Enemy(Fighter):
    def __init__(self, x: int, y: int, enemy_type: str):
        stats = self._get_enemy_stats(enemy_type)
        super().__init__(
            x=x, y=y,
            char=stats['char'],
            color=stats['color'],
            name=stats['name'],
            hp=stats['hp'],
            atk=stats['atk'],
            defense=stats['defense'],
            exp=stats['exp'],
            blocks=True
        )
        self.enemy_type = enemy_type

    def _get_enemy_stats(self, enemy_type: str) -> dict:
        stats = {
            'slime': {
                'char': 's',
                'color': (0, 255, 0),
                'name': '史莱姆',
                'hp': 10,
                'atk': 3,
                'defense': 0,
                'exp': 10
            },
            'goblin': {
                'char': 'g',
                'color': (255, 128, 0),
                'name': '哥布林',
                'hp': 16,
                'atk': 5,
                'defense': 1,
                'exp': 25
            },
            'skeleton': {
                'char': 'k',
                'color': (255, 255, 255),
                'name': '骷髅',
                'hp': 24,
                'atk': 7,
                'defense': 2,
                'exp': 50
            }
        }
        return stats.get(enemy_type, stats['slime'])

    def get_move_towards(self, target_x: int, target_y: int,
                         map_data, entities) -> Tuple[int, int]:
        dx = target_x - self.x
        dy = target_y - self.y

        if abs(dx) > abs(dy):
            step_x = 1 if dx > 0 else -1
            step_y = 0
        else:
            step_x = 0
            step_y = 1 if dy > 0 else -1

        new_x = self.x + step_x
        new_y = self.y + step_y

        if not self._is_blocked(new_x, new_y, map_data, entities):
            return step_x, step_y

        if step_x != 0:
            if not self._is_blocked(self.x, self.y + 1, map_data, entities):
                return 0, 1
            if not self._is_blocked(self.x, self.y - 1, map_data, entities):
                return 0, -1
        elif step_y != 0:
            if not self._is_blocked(self.x + 1, self.y, map_data, entities):
                return 1, 0
            if not self._is_blocked(self.x - 1, self.y, map_data, entities):
                return -1, 0

        return 0, 0

    def _is_blocked(self, x: int, y: int, map_data, entities) -> bool:
        if x < 0 or x >= len(map_data) or y < 0 or y >= len(map_data[0]):
            return True
        if map_data[x][y].blocked:
            return True
        for entity in entities:
            if entity != self and entity.blocks and entity.x == x and entity.y == y:
                return True
        return False

    def is_in_view(self, player_x: int, player_y: int, visible) -> bool:
        return visible[self.x][self.y]
