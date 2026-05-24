from __future__ import annotations

from typing import List, Tuple

from game.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT,
    BAR_WIDTH, PANEL_HEIGHT, PANEL_Y,
    MESSAGE_X, MESSAGE_WIDTH, MESSAGE_HEIGHT,
    COLOR_DARK_WALL, COLOR_DARK_GROUND, COLOR_LIGHT_WALL, COLOR_LIGHT_GROUND
)
from game.entity import Player, Enemy


class Renderer:
    def __init__(self, root_console):
        self.root_console = root_console

    def render_all(self, map_data, player: Player, enemies: List[Enemy],
                   visible, explored, message_log, minimap_enabled: bool = True):
        self._render_map(map_data, visible, explored)
        self._render_entities(player, enemies, visible)
        self._render_panel(player, message_log)
        if minimap_enabled:
            self._render_minimap(explored, player)

    def _render_map(self, map_data, visible, explored) -> None:
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                is_visible = visible[x][y]
                is_explored = explored[x][y]

                if not is_explored:
                    continue

                wall = map_data[x][y].block_sight

                if is_visible:
                    if wall:
                        self.root_console.print(
                            x, y, '#',
                            fg=COLOR_LIGHT_WALL,
                            bg=COLOR_LIGHT_GROUND
                        )
                    else:
                        self.root_console.print(
                            x, y, '.',
                            fg=COLOR_LIGHT_GROUND,
                            bg=(0, 0, 0)
                        )
                elif is_explored:
                    if wall:
                        self.root_console.print(
                            x, y, '#',
                            fg=COLOR_DARK_WALL,
                            bg=COLOR_DARK_GROUND
                        )
                    else:
                        self.root_console.print(
                            x, y, '.',
                            fg=COLOR_DARK_GROUND,
                            bg=(0, 0, 0)
                        )

    def _render_entities(self, player: Player, enemies: List[Enemy],
                         visible) -> None:
        for enemy in enemies:
            if visible[enemy.x][enemy.y]:
                self.root_console.print(
                    enemy.x, enemy.y, enemy.char,
                    fg=enemy.color,
                    bg=(0, 0, 0)
                )

        self.root_console.print(
            player.x, player.y, player.char,
            fg=player.color,
            bg=(0, 0, 0)
        )

    def _render_panel(self, player: Player, message_log) -> None:
        self.root_console.draw_rect(
            0, PANEL_Y, SCREEN_WIDTH, PANEL_HEIGHT,
            ch=' ',
            fg=(255, 255, 255),
            bg=(0, 0, 0)
        )

        self._render_bar(
            1, PANEL_Y + 1, BAR_WIDTH,
            'HP', player.hp, player.max_hp,
            (0, 128, 0), (128, 0, 0)
        )

        self.root_console.print(
            1, PANEL_Y + 2,
            f'ATK: {player.atk}  DEF: {player.defense}  '
            f'Level: {player.floor}  EXP: {player.exp}/{player.level * 100}',
            fg=(255, 255, 255),
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
            if i < MESSAGE_HEIGHT - 1:
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

        self.root_console.draw_rect(
            x, y, width, 1,
            ch=' ',
            fg=(255, 255, 255),
            bg=back_color
        )

        if bar_width > 0:
            self.root_console.draw_rect(
                x, y, bar_width, 1,
                ch=' ',
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
        minimap_scale = 2
        minimap_x = SCREEN_WIDTH - MAP_WIDTH // minimap_scale - 2
        minimap_y = PANEL_Y + 1

        for x in range(0, MAP_WIDTH, minimap_scale):
            for y in range(0, MAP_HEIGHT, minimap_scale):
                if explored[x][y]:
                    minimap_px = minimap_x + x // minimap_scale
                    minimap_py = minimap_y + y // minimap_scale
                    self.root_console.print(
                        minimap_px, minimap_py, '.',
                        fg=(128, 128, 128),
                        bg=(0, 0, 0)
                    )

        player_px = minimap_x + player.x // minimap_scale
        player_py = minimap_y + player.y // minimap_scale
        self.root_console.print(
            player_px, player_py, '@',
            fg=(255, 255, 0),
            bg=(0, 0, 0)
        )

    def clear(self) -> None:
        self.root_console.clear(fg=(255, 255, 255), bg=(0, 0, 0))
