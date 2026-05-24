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

        if isinstance(attacker, Player):
            attacker_hp_info = f'(HP:{attacker.hp}/{attacker.max_hp})'
        else:
            attacker_hp_info = ''

        if isinstance(target, Player):
            target_hp_info = f'(HP:{target.hp}/{target.max_hp})'
        else:
            target_hp_info = f'(剩余HP:{max(0, target.hp)})'

        self.message_log.add(
            f'{attacker.name}{attacker_hp_info} 攻击 {target.name}{target_hp_info}，造成 {actual_damage} 点伤害！',
            (255, 255, 0)
        )

        if target.is_dead():
            self.message_log.add(
                f'✗ {target.name} 被击败了！',
                (255, 0, 0)
            )
            if isinstance(attacker, Player) and isinstance(target, Enemy):
                old_level = attacker.level
                attacker.gain_exp(target.exp)
                self.message_log.add(
                    f'✓ 获得 {target.exp} 点经验值！',
                    (0, 255, 0)
                )

                if attacker.level > old_level:
                    level_diff = attacker.level - old_level
                    for _ in range(level_diff):
                        self.message_log.add(
                            f'★ 升级了！当前等级：{attacker.level}！HP+10 ATK+2 DEF+1',
                            (255, 0, 255)
                        )

                exp_needed = attacker.level * 100
                exp_remaining = exp_needed - attacker.exp
                if exp_remaining > 0:
                    self.message_log.add(
                        f'距离下一级还需 {exp_remaining} 点经验',
                        (128, 255, 255)
                    )
            return True

        return False

    def get_enemy_at(self, enemies: List[Enemy],
                     x: int, y: int) -> Optional[Enemy]:
        for enemy in enemies:
            if enemy.x == x and enemy.y == y and not enemy.is_dead():
                return enemy
        return None
