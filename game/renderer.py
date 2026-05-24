from __future__ import annotations

from typing import List, Tuple

from game.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT,
    VIEWPORT_WIDTH, VIEWPORT_HEIGHT,
    BAR_WIDTH, PANEL_HEIGHT, PANEL_Y,
    MESSAGE_X, MESSAGE_WIDTH, MESSAGE_HEIGHT,
    COLOR_DARK_WALL, COLOR_DARK_GROUND, COLOR_LIGHT_WALL, COLOR_LIGHT_GROUND
)
from game.entity import Player, Enemy


class Renderer:
    def __init__(self, root_console):
        self.root_console = root_console
        self.camera_x = 0
        self.camera_y = 0

    def update_camera(self, player_x: int, player_y: int) -> None:
        target_x = player_x - VIEWPORT_WIDTH // 2
        target_y = player_y - VIEWPORT_HEIGHT // 2

        target_x = max(0, min(target_x, MAP_WIDTH - VIEWPORT_WIDTH))
        target_y = max(0, min(target_y, MAP_HEIGHT - VIEWPORT_HEIGHT))

        if MAP_WIDTH < VIEWPORT_WIDTH:
            target_x = 0
        if MAP_HEIGHT < VIEWPORT_HEIGHT:
            target_y = 0

        self.camera_x = target_x
        self.camera_y = target_y

    def render_all(self, map_data, player: Player, enemies: List[Enemy],
                   visible, explored, message_log, minimap_enabled: bool = True):
        self.update_camera(player.x, player.y)
        self._render_map(map_data, visible, explored)
        self._render_entities(player, enemies, visible)
        self._render_panel(player, message_log)
        if minimap_enabled:
            self._render_minimap(explored, player)

    def _to_screen(self, x: int, y: int) -> Tuple[int, int]:
        return x - self.camera_x, y - self.camera_y

    def _is_in_viewport(self, screen_x: int, screen_y: int) -> bool:
        return 0 <= screen_x < VIEWPORT_WIDTH and 0 <= screen_y < VIEWPORT_HEIGHT

    def _render_map(self, map_data, visible, explored) -> None:
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                screen_x, screen_y = self._to_screen(x, y)
                if not self._is_in_viewport(screen_x, screen_y):
                    continue

                is_visible = visible[x][y]
                is_explored = explored[x][y]

                if not is_explored:
                    self.root_console.print(
                        screen_x, screen_y, ' ',
                        fg=(0, 0, 0),
                        bg=(0, 0, 0)
                    )
                    continue

                wall = map_data[x][y].block_sight

                if is_visible:
                    if wall:
                        self.root_console.print(
                            screen_x, screen_y, '#',
                            fg=COLOR_LIGHT_WALL,
                            bg=COLOR_LIGHT_GROUND
                        )
                    else:
                        self.root_console.print(
                            screen_x, screen_y, '.',
                            fg=COLOR_LIGHT_GROUND,
                            bg=(0, 0, 0)
                        )
                elif is_explored:
                    if wall:
                        self.root_console.print(
                            screen_x, screen_y, '#',
                            fg=COLOR_DARK_WALL,
                            bg=COLOR_DARK_GROUND
                        )
                    else:
                        self.root_console.print(
                            screen_x, screen_y, '.',
                            fg=COLOR_DARK_GROUND,
                            bg=(0, 0, 0)
                        )

    def _render_entities(self, player: Player, enemies: List[Enemy],
                         visible) -> None:
        for enemy in enemies:
            if visible[enemy.x][enemy.y]:
                screen_x, screen_y = self._to_screen(enemy.x, enemy.y)
                if self._is_in_viewport(screen_x, screen_y):
                    self.root_console.print(
                        screen_x, screen_y, enemy.char,
                        fg=enemy.color,
                        bg=(0, 0, 0)
                    )

        screen_x, screen_y = self._to_screen(player.x, player.y)
        if self._is_in_viewport(screen_x, screen_y):
            self.root_console.print(
                screen_x, screen_y, player.char,
                fg=player.color,
                bg=(0, 0, 0)
            )

    def _render_panel(self, player: Player, message_log) -> None:
        for x in range(SCREEN_WIDTH):
            for y in range(PANEL_Y, PANEL_Y + PANEL_HEIGHT):
                self.root_console.print(
                    x, y, ' ',
                    fg=(255, 255, 255),
                    bg=(0, 0, 0)
                )

        self._render_bar(
            1, PANEL_Y + 1, BAR_WIDTH,
            'HP', player.hp, player.max_hp,
            (0, 128, 0), (128, 0, 0)
        )

        exp_needed = player.level * 100
        exp_remaining = exp_needed - player.exp
        self.root_console.print(
            1, PANEL_Y + 3,
            f'ATK: {player.atk}  DEF: {player.defense}',
            fg=(255, 255, 255),
            bg=(0, 0, 0)
        )

        self.root_console.print(
            1, PANEL_Y + 4,
            f'等级: {player.level}  楼层: {player.floor}',
            fg=(0, 255, 255),
            bg=(0, 0, 0)
        )

        self.root_console.print(
            1, PANEL_Y + 5,
            f'经验: {player.exp}/{exp_needed} (还需: {exp_remaining})',
            fg=(255, 255, 0),
            bg=(0, 0, 0)
        )

        self.root_console.print(
            MESSAGE_X, PANEL_Y + 1,
            '战斗日志:',
            fg=(255, 255, 0),
            bg=(0, 0, 0)
        )

        messages = message_log.get_recent(MESSAGE_HEIGHT)
        for i, (msg_text, msg_color) in enumerate(messages):
            self.root_console.print(
                MESSAGE_X, PANEL_Y + 2 + i,
                msg_text[:MESSAGE_WIDTH],
                fg=msg_color,
                bg=(0, 0, 0)
            )

    def _render_bar(self, x: int, y: int, width: int, text: str,
                    value: int, maximum: int,
                    bar_color: Tuple[int, int, int],
                    back_color: Tuple[int, int, int]) -> None:
        bar_width = int(float(value) / maximum * width)

        for i in range(width):
            self.root_console.print(
                x + i, y, ' ',
                fg=(255, 255, 255),
                bg=back_color
            )

        if bar_width > 0:
            for i in range(bar_width):
                self.root_console.print(
                    x + i, y, ' ',
                    fg=(255, 255, 255),
                    bg=bar_color
                )

        self.root_console.print(
            x, y,
            f'{text}: {value}/{maximum}',
            fg=(255, 255, 255),
            bg=(0, 0, 0)
        )

    def _render_minimap(self, explored, player: Player) -> None:
        minimap_scale = 3
        minimap_width = MAP_WIDTH // minimap_scale
        minimap_height = MAP_HEIGHT // minimap_scale
        minimap_x = SCREEN_WIDTH - minimap_width - 1
        minimap_y = PANEL_Y + 1

        for x in range(0, MAP_WIDTH, minimap_scale):
            for y in range(0, MAP_HEIGHT, minimap_scale):
                if explored[x][y]:
                    minimap_px = minimap_x + x // minimap_scale
                    minimap_py = minimap_y + y // minimap_scale
                    if 0 <= minimap_px < SCREEN_WIDTH and 0 <= minimap_py < PANEL_Y + PANEL_HEIGHT:
                        self.root_console.print(
                            minimap_px, minimap_py, '.',
                            fg=(128, 128, 128),
                            bg=(0, 0, 0)
                        )

        player_px = minimap_x + player.x // minimap_scale
        player_py = minimap_y + player.y // minimap_scale
        if 0 <= player_px < SCREEN_WIDTH and 0 <= player_py < PANEL_Y + PANEL_HEIGHT:
            self.root_console.print(
                player_px, player_py, '@',
                fg=(255, 255, 0),
                bg=(0, 0, 0)
            )

    def clear(self) -> None:
        self.root_console.clear(fg=(255, 255, 255), bg=(0, 0, 0))
