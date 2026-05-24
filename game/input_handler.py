from __future__ import annotations

from typing import Tuple, Optional
import tcod.event


class InputHandler:
    def __init__(self):
        self.game_state = 'playing'
        self.previous_game_state = 'playing'

    def handle_keys(self, event: tcod.event.Event) -> Optional[dict]:
        if isinstance(event, tcod.event.Quit):
            return {'action': 'exit'}

        if isinstance(event, tcod.event.KeyDown):
            if self.game_state == 'playing':
                return self._handle_playing(event)
            elif self.game_state == 'game_over':
                return self._handle_game_over(event)
            elif self.game_state == 'victory':
                return self._handle_game_over(event)

        return {}

    def _handle_playing(self, event: tcod.event.KeyDown) -> Optional[dict]:
        key = event.sym

        if key in (tcod.event.K_UP, tcod.event.K_k, tcod.event.K_w):
            return {'move': (0, -1)}
        elif key in (tcod.event.K_DOWN, tcod.event.K_j, tcod.event.K_s):
            return {'move': (0, 1)}
        elif key in (tcod.event.K_LEFT, tcod.event.K_h, tcod.event.K_a):
            return {'move': (-1, 0)}
        elif key in (tcod.event.K_RIGHT, tcod.event.K_l, tcod.event.K_d):
            return {'move': (1, 0)}
        elif key in (tcod.event.K_y,):
            return {'move': (-1, -1)}
        elif key in (tcod.event.K_u,):
            return {'move': (1, -1)}
        elif key in (tcod.event.K_b,):
            return {'move': (-1, 1)}
        elif key in (tcod.event.K_n,):
            return {'move': (1, 1)}

        if key in (tcod.event.K_RETURN, tcod.event.K_KP_ENTER):
            pass

        if key in (tcod.event.K_ESCAPE,):
            return {'action': 'exit'}

        if key in (tcod.event.K_PERIOD,):
            return {'action': 'wait'}

        return {}

    def _handle_game_over(self, event: tcod.event.KeyDown) -> Optional[dict]:
        if event.sym in (tcod.event.K_RETURN, tcod.event.K_KP_ENTER, tcod.event.K_ESCAPE):
            return {'action': 'restart'}
        return {}
