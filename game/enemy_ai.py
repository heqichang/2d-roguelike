from __future__ import annotations

from typing import List, Tuple

from game.entity import Player, Enemy
from game.message_log import MessageLog
from game.combat import CombatSystem


class EnemyAI:
    def __init__(self, combat_system: CombatSystem, message_log: MessageLog):
        self.combat_system = combat_system
        self.message_log = message_log

    def process_enemies(self, enemies: List[Enemy], player: Player,
                        map_data, visible) -> List[Enemy]:
        dead_enemies = []

        for enemy in enemies:
            if enemy.is_dead():
                continue

            if not visible[enemy.x][enemy.y]:
                continue

            dx = player.x - enemy.x
            dy = player.y - enemy.y
            distance = max(abs(dx), abs(dy))

            if distance <= 1:
                self.combat_system.attack(enemy, player)
            else:
                move_dx, move_dy = enemy.get_move_towards(
                    player.x, player.y, map_data, enemies + [player]
                )

                target_x = enemy.x + move_dx
                target_y = enemy.y + move_dy

                if target_x == player.x and target_y == player.y:
                    self.combat_system.attack(enemy, player)
                else:
                    enemy.move(move_dx, move_dy)

        return [e for e in enemies if not e.is_dead()]
