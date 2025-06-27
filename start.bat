@echo off
REM 设置控制台编码为UTF-8
chcp 65001 >nul 2>&1

title PyProxy - Trojan代理客户端
echo.
echo ====================================
echo      PyProxy - Trojan代理客户端
echo ====================================
echo.

REM 检查配置文件
if not exist configs\config.yaml (
    echo ❌ 错误: 配置文件 configs\config.yaml 不存在
    echo 💡 请运行设置脚本: python scripts\setup.py
    echo.
    pause
    exit /b 1
)

REM 启动代理客户端
echo 🚀 正在启动代理客户端...
echo.
python scripts\start.py -c configs\config.yaml

echo.
echo 👋 代理客户端已停止
pause 