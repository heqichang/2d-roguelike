from __future__ import annotations

from typing import Tuple, Optional
import tcod.event
from tcod.event import KeySym


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

        if key in (KeySym.UP, KeySym.K, KeySym.W):
            return {'move': (0, -1)}
        elif key in (KeySym.DOWN, KeySym.J, KeySym.S):
            return {'move': (0, 1)}
        elif key in (KeySym.LEFT, KeySym.H, KeySym.A):
            return {'move': (-1, 0)}
        elif key in (KeySym.RIGHT, KeySym.L, KeySym.D):
            return {'move': (1, 0)}
        elif key in (KeySym.Y,):
            return {'move': (-1, -1)}
        elif key in (KeySym.U,):
            return {'move': (1, -1)}
        elif key in (KeySym.B,):
            return {'move': (-1, 1)}
        elif key in (KeySym.N,):
            return {'move': (1, 1)}

        if key in (KeySym.RETURN, KeySym.KP_ENTER):
            pass

        if key in (KeySym.ESCAPE,):
            return {'action': 'exit'}

        if key in (KeySym.PERIOD,):
            return {'action': 'wait'}

        return {}

    def _handle_game_over(self, event: tcod.event.KeyDown) -> Optional[dict]:
        if event.sym in (KeySym.RETURN, KeySym.KP_ENTER, KeySym.ESCAPE):
            return {'action': 'restart'}
        return {}
