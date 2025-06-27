@echo off
REM 设置控制台编码为UTF-8
chcp 65001 >nul 2>&1

title PyProxy - 综合测试工具
echo.
echo ====================================
echo     PyProxy - 综合测试工具
echo ====================================
echo.

REM 运行综合测试
echo 🧪 正在启动综合测试...
echo.
python tests\comprehensive_test.py

echo.
echo 📊 测试已完成
pause 