@echo off
chcp 65001 >nul
echo ============================================
echo    2D Roguelike 地牢探险游戏
echo ============================================
echo.

echo [1/2] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到 Python，请先安装 Python 3.8 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Python 环境已就绪

echo.
echo [2/2] 检查依赖...
python -c "import tcod" >nul 2>&1
if errorlevel 1 (
    echo 正在安装 tcod 依赖...
    pip install tcod
    if errorlevel 1 (
        echo 错误: 安装依赖失败，请手动运行: pip install tcod
        pause
        exit /b 1
    )
)
echo 依赖已就绪

echo.
echo 启动游戏...
python main.py
pause
