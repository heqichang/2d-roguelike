from __future__ import annotations

import random
import sys
from typing import List

import tcod
import tcod.event

from game.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT,
    VIEWPORT_WIDTH, VIEWPORT_HEIGHT,
    MAX_MONSTERS_PER_ROOM
)
from game.dungeon_generator import DungeonGenerator
from game.entity import Player, Enemy
from game.fov import FOVCalculator
from game.message_log import MessageLog
from game.combat import CombatSystem
from game.enemy_ai import EnemyAI
from game.input_handler import InputHandler
from game.renderer import Renderer


class Game:
    def __init__(self):
        self.tileset = tcod.tileset.load_tilesheet(
            "data/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
        )
        self.context = tcod.context.new(
            columns=SCREEN_WIDTH,
            rows=SCREEN_HEIGHT,
            title='2D Roguelike 地牢探险',
            tileset=self.tileset,
            vsync=True
        )
        self.root_console = tcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order='F')

        self.dungeon = DungeonGenerator()
        self.player: Player = None
        self.enemies: List[Enemy] = []
        self.fov = FOVCalculator()
        self.visible = None
        self.explored = None
        self.message_log = MessageLog()
        self.combat = CombatSystem(self.message_log)
        self.enemy_ai = EnemyAI(self.combat, self.message_log)
        self.input_handler = InputHandler()
        self.renderer = Renderer(self.root_console)
        self.game_state = 'playing'
        self.floor_level = 1

    def initialize(self) -> None:
        self.dungeon.generate(self.floor_level)
        start_x, start_y = self.dungeon.start_pos
        self.player = Player(start_x, start_y)
        self.player.floor = self.floor_level

        self._spawn_enemies()

        self.visible = self.fov.calculate(
            self.dungeon.map, self.player.x, self.player.y
        )
        self.explored = [
            [False for _ in range(MAP_HEIGHT)]
            for _ in range(MAP_WIDTH)
        ]
        self._update_explored()

        self.message_log.clear()
        self.message_log.add(
            '欢迎来到地牢！使用方向键或WASD移动。',
            (255, 255, 0)
        )
        self.message_log.add(
            '走向敌人进行攻击。寻找楼梯>进入下一层。',
            (255, 255, 255)
        )

    def _spawn_enemies(self) -> None:
        self.enemies = []
        for room in self.dungeon.rooms[1:]:
            num_monsters = random.randint(0, MAX_MONSTERS_PER_ROOM)
            for _ in range(num_monsters):
                x = random.randint(room.x1 + 1, room.x2 - 1)
                y = random.randint(room.y1 + 1, room.y2 - 1)

                if not self._is_position_occupied(x, y):
                    monster_type = self._random_monster_type()
                    enemy = Enemy(x, y, monster_type)
                    self.enemies.append(enemy)

    def _random_monster_type(self) -> str:
        rand = random.random()
        if self.floor_level == 1:
            if rand < 0.7:
                return 'slime'
            elif rand < 0.9:
                return 'goblin'
            else:
                return 'skeleton'
        elif self.floor_level == 2:
            if rand < 0.4:
                return 'slime'
            elif rand < 0.8:
                return 'goblin'
            else:
                return 'skeleton'
        else:
            if rand < 0.2:
                return 'slime'
            elif rand < 0.5:
                return 'goblin'
            else:
                return 'skeleton'

    def _is_position_occupied(self, x: int, y: int) -> bool:
        if self.player and self.player.x == x and self.player.y == y:
            return True
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y:
                return True
        return False

    def _update_explored(self) -> None:
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if self.visible[x][y]:
                    self.explored[x][y] = True

    def next_floor(self) -> None:
        self.floor_level += 1
        self.player.floor = self.floor_level
        self.dungeon.generate(self.floor_level)

        start_x, start_y = self.dungeon.start_pos
        self.player.x = start_x
        self.player.y = start_y

        self._spawn_enemies()

        self.visible = self.fov.calculate(
            self.dungeon.map, self.player.x, self.player.y
        )
        self.explored = [
            [False for _ in range(MAP_HEIGHT)]
            for _ in range(MAP_WIDTH)
        ]
        self._update_explored()

        self.player.heal(10)

        self.message_log.add(
            f'你进入了第 {self.floor_level} 层！',
            (0, 255, 0)
        )

    def handle_player_move(self, dx: int, dy: int) -> bool:
        new_x = self.player.x + dx
        new_y = self.player.y + dy

        if new_x == self.dungeon.stairs_pos[0] and \
           new_y == self.dungeon.stairs_pos[1]:
            self.next_floor()
            return True

        enemy = self.combat.get_enemy_at(self.enemies, new_x, new_y)
        if enemy:
            self.combat.attack(self.player, enemy)
            if enemy.is_dead():
                self.enemies.remove(enemy)
            return True

        if not self.dungeon.is_blocked(new_x, new_y):
            self.player.move(dx, dy)
            return True

        return False

    def handle_enemy_turn(self) -> None:
        self.enemies = self.enemy_ai.process_enemies(
            self.enemies, self.player, self.dungeon.map, self.visible
        )

        if self.player.is_dead():
            self.game_state = 'game_over'
            self.input_handler.game_state = 'game_over'
            self.message_log.add(
                '你死了！按回车键重新开始。',
                (255, 0, 0)
            )

    def run(self) -> None:
        self.initialize()

        while True:
            self.root_console.clear(fg=(255, 255, 255), bg=(0, 0, 0))

            if self.game_state == 'playing':
                self.renderer.render_all(
                    self.dungeon.map, self.player, self.enemies,
                    self.visible, self.explored, self.message_log
                )

                stairs_x, stairs_y = self.dungeon.stairs_pos
                if self.explored[stairs_x][stairs_y]:
                    screen_stairs_x = stairs_x - self.renderer.camera_x
                    screen_stairs_y = stairs_y - self.renderer.camera_y
                    if 0 <= screen_stairs_x < VIEWPORT_WIDTH and 0 <= screen_stairs_y < VIEWPORT_HEIGHT:
                        stair_char = '>'
                        stair_color = (255, 255, 0)
                        if self.visible[stairs_x][stairs_y]:
                            self.root_console.print(
                                screen_stairs_x, screen_stairs_y, stair_char,
                                fg=stair_color, bg=(0, 0, 0)
                            )
                        else:
                            self.root_console.print(
                                screen_stairs_x, screen_stairs_y, stair_char,
                                fg=(128, 128, 0), bg=(0, 0, 0)
                            )

            elif self.game_state == 'game_over':
                self._render_game_over()

            self.context.present(self.root_console)

            for event in tcod.event.wait():
                action = self.input_handler.handle_keys(event)

                if action is None:
                    continue

                if action.get('action') == 'exit':
                    self.context.close()
                    return

                if action.get('action') == 'restart':
                    self.floor_level = 1
                    self.game_state = 'playing'
                    self.input_handler.game_state = 'playing'
                    self.initialize()
                    continue

                if 'move' in action and self.game_state == 'playing':
                    dx, dy = action['move']
                    turn_taken = self.handle_player_move(dx, dy)

                    if turn_taken:
                        self.visible = self.fov.calculate(
                            self.dungeon.map, self.player.x, self.player.y
                        )
                        self._update_explored()
                        self.handle_enemy_turn()

                if action.get('action') == 'wait' and self.game_state == 'playing':
                    self.visible = self.fov.calculate(
                        self.dungeon.map, self.player.x, self.player.y
                    )
                    self._update_explored()
                    self.handle_enemy_turn()

    def _render_game_over(self) -> None:
        title = '游戏结束'
        msg1 = f'你到达了第 {self.floor_level} 层'
        msg2 = f'最终等级: {self.player.level}'
        msg3 = '按回车键或ESC重新开始'

        title_x = SCREEN_WIDTH // 2 - len(title) // 2
        msg1_x = SCREEN_WIDTH // 2 - len(msg1) // 2
        msg2_x = SCREEN_WIDTH // 2 - len(msg2) // 2
        msg3_x = SCREEN_WIDTH // 2 - len(msg3) // 2

        self.root_console.clear(fg=(255, 255, 255), bg=(0, 0, 0))

        self.root_console.print(
            title_x, SCREEN_HEIGHT // 2 - 3, title,
            fg=(255, 0, 0), bg=(0, 0, 0)
        )
        self.root_console.print(
            msg1_x, SCREEN_HEIGHT // 2 - 1, msg1,
            fg=(255, 255, 255), bg=(0, 0, 0)
        )
        self.root_console.print(
            msg2_x, SCREEN_HEIGHT // 2, msg2,
            fg=(0, 255, 255), bg=(0, 0, 0)
        )
        self.root_console.print(
            msg3_x, SCREEN_HEIGHT // 2 + 2, msg3,
            fg=(255, 255, 0), bg=(0, 0, 0)
        )


def main():
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
