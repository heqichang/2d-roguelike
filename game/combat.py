from __future__ import annotations

from typing import List, Optional, Tuple

from game.entity import Player, Enemy, Fighter
from game.message_log import MessageLog


class CombatSystem:
    def __init__(self, message_log: MessageLog):
        self.message_log = message_log

    def attack(self, attacker: Fighter, target: Fighter) -> bool:
        damage = attacker.atk
        actual_damage = target.take_damage(damage)

        self.message_log.add(
            f'{attacker.name}攻击{target.name}，造成{actual_damage}点伤害！',
            (255, 255, 0)
        )

        if target.is_dead():
            self.message_log.add(
                f'{target.name}被击败了！',
                (255, 0, 0)
            )
            if isinstance(attacker, Player) and isinstance(target, Enemy):
                attacker.gain_exp(target.exp)
                self.message_log.add(
                    f'获得{target.exp}点经验值！',
                    (0, 255, 0)
                )
            return True

        return False

    def get_enemy_at(self, enemies: List[Enemy],
                     x: int, y: int) -> Optional[Enemy]:
        for enemy in enemies:
            if enemy.x == x and enemy.y == y and not enemy.is_dead():
                return enemy
        return None
