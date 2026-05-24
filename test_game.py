from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.dungeon_generator import DungeonGenerator, Tile, Rect
from game.entity import Player, Enemy
from game.fov import FOVCalculator
from game.message_log import MessageLog
from game.combat import CombatSystem


def test_dungeon_generation():
    print("Testing dungeon generation...")
    dungeon = DungeonGenerator()
    dungeon.generate(floor_level=1)

    assert dungeon.start_pos != (0, 0), "Start position should not be (0,0)"
    assert dungeon.stairs_pos != (0, 0), "Stairs position should not be (0,0)"
    assert len(dungeon.rooms) > 0, "Should have at least one room"

    start_x, start_y = dungeon.start_pos
    assert not dungeon.is_blocked(start_x, start_y), "Start position should not be blocked"

    print(f"  Dungeon generated with {len(dungeon.rooms)} rooms")
    print(f"  Start position: {dungeon.start_pos}")
    print(f"  Stairs position: {dungeon.stairs_pos}")
    print("  PASSED!")


def test_player_creation():
    print("Testing player creation...")
    player = Player(10, 10)

    assert player.x == 10, "Player X position should be 10"
    assert player.y == 10, "Player Y position should be 10"
    assert player.char == '@', "Player char should be '@'"
    assert player.hp == 30, "Player HP should be 30"
    assert player.atk == 5, "Player ATK should be 5"
    assert player.defense == 2, "Player DEF should be 2"
    assert player.level == 1, "Player level should be 1"

    print(f"  Player created at ({player.x}, {player.y})")
    print(f"  HP: {player.hp}/{player.max_hp}, ATK: {player.atk}, DEF: {player.defense}")
    print("  PASSED!")


def test_enemy_creation():
    print("Testing enemy creation...")

    enemies = {
        'slime': Enemy(5, 5, 'slime'),
        'goblin': Enemy(10, 10, 'goblin'),
        'skeleton': Enemy(15, 15, 'skeleton'),
    }

    assert enemies['slime'].hp == 10, "Slime HP should be 10"
    assert enemies['goblin'].hp == 16, "Goblin HP should be 16"
    assert enemies['skeleton'].hp == 24, "Skeleton HP should be 24"

    assert enemies['slime'].atk == 3, "Slime ATK should be 3"
    assert enemies['goblin'].atk == 5, "Goblin ATK should be 5"
    assert enemies['skeleton'].atk == 7, "Skeleton ATK should be 7"

    print(f"  Slime: HP={enemies['slime'].hp}, ATK={enemies['slime'].atk}, DEF={enemies['slime'].defense}")
    print(f"  Goblin: HP={enemies['goblin'].hp}, ATK={enemies['goblin'].atk}, DEF={enemies['goblin'].defense}")
    print(f"  Skeleton: HP={enemies['skeleton'].hp}, ATK={enemies['skeleton'].atk}, DEF={enemies['skeleton'].defense}")
    print("  PASSED!")


def test_combat():
    print("Testing combat system...")
    log = MessageLog()
    combat = CombatSystem(log)

    player = Player(10, 10)
    slime = Enemy(11, 10, 'slime')

    initial_slime_hp = slime.hp
    combat.attack(player, slime)

    assert slime.hp < initial_slime_hp, "Slime should take damage"
    assert len(log.messages) > 0, "Message log should have messages"

    print(f"  Player attacks slime: {initial_slime_hp} -> {slime.hp}")
    print(f"  Log messages: {log.messages[-1][0]}")
    print("  PASSED!")


def test_fov():
    print("Testing FOV calculation...")
    dungeon = DungeonGenerator()
    dungeon.generate(floor_level=1)

    fov = FOVCalculator()
    start_x, start_y = dungeon.start_pos
    visible = fov.calculate(dungeon.map, start_x, start_y)

    assert visible[start_x][start_y], "Player position should be visible"

    visible_count = sum(
        1 for x in range(len(visible))
        for y in range(len(visible[0]))
        if visible[x][y]
    )

    print(f"  FOV calculated from ({start_x}, {start_y})")
    print(f"  Visible tiles: {visible_count}")
    print("  PASSED!")


def test_message_log():
    print("Testing message log...")
    log = MessageLog()

    for i in range(10):
        log.add(f"Message {i}", (255, 255, 255))

    assert len(log.messages) == 10, "Should have 10 messages"

    recent = log.get_recent(5)
    assert len(recent) == 5, "Should return 5 recent messages"
    assert recent[0][0] == "Message 5", "First recent message should be 'Message 5'"

    print(f"  Log has {len(log.messages)} messages")
    print(f"  Recent messages: {[m[0] for m in recent]}")
    print("  PASSED!")


def test_level_up():
    print("Testing level up...")
    player = Player(10, 10)
    initial_max_hp = player.max_hp
    initial_atk = player.atk

    player.gain_exp(100)

    assert player.level == 2, "Player should level up to 2"
    assert player.max_hp > initial_max_hp, "Max HP should increase"
    assert player.atk > initial_atk, "ATK should increase"

    print(f"  Level: {player.level}, HP: {player.max_hp}, ATK: {player.atk}")
    print("  PASSED!")


def main():
    print("=" * 60)
    print("Running 2D Roguelike Game Tests")
    print("=" * 60)

    tests = [
        ("Dungeon Generation", test_dungeon_generation),
        ("Player Creation", test_player_creation),
        ("Enemy Creation", test_enemy_creation),
        ("Combat System", test_combat),
        ("FOV Calculation", test_fov),
        ("Message Log", test_message_log),
        ("Level Up", test_level_up),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            print(f"\n[{name}]", end=" ")
            test_func()
            passed += 1
        except Exception as e:
            print(f"FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
