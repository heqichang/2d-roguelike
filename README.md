# 2D Roguelike 地牢探险游戏

一款使用 Python 和 tcod (libtcod) 开发的 2D 回合制 Roguelike 地牢探险游戏。

## 功能特性

### 地牢生成
- 使用 BSP (二叉空间分割) 算法随机生成房间
- 房间之间通过走廊连接
- 每层都有楼梯通往下一层
- 战争迷雾系统（仅显示已探索区域）
- 墙壁、地板、门等基础地形

### 玩家系统
- 键盘移动（方向键或 WASD）
- 回合制移动（玩家行动后敌人行动）
- 碰撞检测（不可穿墙）
- 基础属性：生命值(HP)、攻击力(ATK)、防御力(DEF)
- 视野范围（基于光线投射的视野计算）
- 升级系统（击败敌人获得经验值）

### 战斗系统
- 移动到敌人格子触发攻击
- 伤害计算：ATK - DEF（最低 1 点伤害）
- 战斗日志（文字记录发生了什么）
- 永久死亡机制

### 敌人类型
- 史莱姆（低 HP、低 ATK）
- 哥布林（中 HP、中 ATK）
- 骷髅（高 HP、高 ATK）
- 敌人 AI：简单追踪（检测到玩家后向玩家移动）

### UI 系统
- 游戏主画面（地牢视图）
- 状态栏（HP、ATK、DEF、层数）
- 战斗日志面板
- 小地图（已探索区域）

## 安装说明

### 前提条件
- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

1. 克隆或下载此项目

2. 安装依赖：
```bash
pip install tcod
```

或使用 requirements.txt：
```bash
pip install -r requirements.txt
```

## 运行游戏

```bash
python main.py
```

## 操作说明

| 按键 | 功能 |
|------|------|
| 方向键 / WASD | 移动 |
| Y / U / B / N | 斜向移动 |
| . | 等待一回合 |
| ESC | 退出游戏 |

## 游戏机制

- 每层难度递增，敌人更强更多
- 找到楼梯(>)进入下一层
- 击败敌人获得经验值升级
- 死亡后游戏结束，需要重新开始

## 运行测试

```bash
python test_game.py
```

## 项目结构

```
2d-roguelike/
├── main.py                 # 主游戏入口
├── test_game.py            # 测试文件
├── requirements.txt        # 依赖列表
├── game/
│   ├── __init__.py
│   ├── constants.py        # 游戏常量配置
│   ├── dungeon_generator.py # 地牢生成系统（BSP算法）
│   ├── entity.py           # 实体系统（玩家、敌人）
│   ├── fov.py              # 视野计算系统
│   ├── combat.py           # 战斗系统
│   ├── enemy_ai.py         # 敌人AI系统
│   ├── message_log.py      # 消息日志系统
│   ├── input_handler.py    # 输入处理系统
│   └── renderer.py         # 渲染系统
└── README.md
```

## 技术栈

- Python 3.8+
- tcod (libtcod) - Roguelike 游戏库

## 开发说明

### 地牢生成算法
使用 BSP（二叉空间分割）算法将地图分割成多个区域，在每个叶子节点创建房间，然后使用走廊连接相邻房间。

### 视野计算
使用光线投射（Raycasting）算法计算玩家视野，模拟战争迷雾效果。

### 回合制系统
玩家每次移动或等待消耗一回合，随后所有敌人行动。
