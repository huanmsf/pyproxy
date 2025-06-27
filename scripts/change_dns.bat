@echo off
chcp 65001 >nul
title DNS服务器切换工具 (修复版)

echo.
echo 🌐 DNS服务器切换工具 (修复版)
echo ==========================================

echo.
echo 🔍 检测到的网络接口:
echo   - WLAN (无线网络) - 活跃
echo   - 以太网 - 断开连接
echo.

echo 📋 可选DNS服务器:
echo   1. Cloudflare (1.1.1.1, 1.0.0.1)
echo   2. Google     (8.8.8.8, 8.8.4.4)  
echo   3. 阿里云     (223.5.5.5, 223.6.6.6)
echo   4. 腾讯云     (119.29.29.29, 182.254.116.116)
echo   5. 恢复默认   (自动获取)
echo   0. 退出
echo.

set /p choice=请选择要切换的DNS服务器 (1-5): 

echo.

if "%choice%"=="1" (
    echo 🔄 切换到Cloudflare DNS...
    call :setDNS "1.1.1.1" "1.0.0.1" "Cloudflare"
) else if "%choice%"=="2" (
    echo 🔄 切换到Google DNS...
    call :setDNS "8.8.8.8" "8.8.4.4" "Google"
) else if "%choice%"=="3" (
    echo 🔄 切换到阿里云DNS...
    call :setDNS "223.5.5.5" "223.6.6.6" "阿里云"
) else if "%choice%"=="4" (
    echo 🔄 切换到腾讯云DNS...
    call :setDNS "119.29.29.29" "182.254.116.116" "腾讯云"
) else if "%choice%"=="5" (
    echo 🔄 恢复自动获取DNS...
    call :resetDNS
) else if "%choice%"=="0" (
    echo 👋 退出
    exit /b 0
) else (
    echo ❌ 无效选择
    pause
    exit /b 1
)

echo.
echo 🧹 清理DNS缓存...
ipconfig /flushdns >nul 2>&1
echo ✅ DNS缓存已清理

echo.
echo 🔍 验证DNS设置...
echo.
nslookup google.com 2>nul | findstr "Server\|Address"

echo.
echo ✅ DNS切换完成！
echo.
echo 💡 提示:
echo   - 新DNS设置可能需要几秒钟生效
echo   - 建议重启浏览器以使用新DNS
echo   - 配合代理工具使用效果更佳
echo.

pause
exit /b 0

:setDNS
set "dns1=%~1"
set "dns2=%~2"
set "provider=%~3"

echo 正在设置 %provider% DNS (%dns1%, %dns2%)...
echo.

REM 为WLAN接口设置DNS
echo 配置无线网络接口 (WLAN)...
netsh interface ip set dns "WLAN" static %dns1% 2>nul
if errorlevel 1 (
    echo   ⚠️ 可能需要管理员权限
) else (
    echo   ✅ 主DNS设置成功: %dns1%
    
    netsh interface ip add dns "WLAN" %dns2% index=2 2>nul
    if not errorlevel 1 (
        echo   ✅ 备用DNS设置成功: %dns2%
    )
)

REM 同时尝试设置其他可能的接口
for %%i in ("以太网" "以太网 2" "以太网 3") do (
    netsh interface ip set dns %%i static %dns1% >nul 2>&1
    if not errorlevel 1 (
        echo   ✅ %%i 也已配置
        netsh interface ip add dns %%i %dns2% index=2 >nul 2>&1
    )
)

echo.
echo ✅ %provider% DNS设置完成
goto :eof

:resetDNS
echo 正在恢复自动获取DNS设置...
echo.

REM 重置WLAN接口
echo 重置无线网络接口 (WLAN)...
netsh interface ip set dns "WLAN" dhcp 2>nul
if errorlevel 1 (
    echo   ⚠️ 可能需要管理员权限
) else (
    echo   ✅ WLAN接口已重置为自动获取
)

REM 同时重置其他接口
for %%i in ("以太网" "以太网 2" "以太网 3") do (
    netsh interface ip set dns %%i dhcp >nul 2>&1
    if not errorlevel 1 (
        echo   ✅ %%i 也已重置
    )
)

echo.
echo ✅ DNS设置已恢复为自动获取
goto :eof 