@echo off
chcp 65001 >nul
title Windows 垃圾清理 Bot
color 0a

echo ================================================
echo            🧹 Windows 系统垃圾清理
echo ================================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️ 建议以管理员身份运行此脚本！
    echo.
)

echo 即将清理以下内容：
echo   [1] Windows 临时文件
echo   [2] 用户临时文件
echo   [3] 浏览器缓存 (Chrome/Edge)
echo   [4] Windows 更新缓存
echo   [5] 日志文件
echo   [6] 回收站
echo.
echo ================================================

:: 确认
set /p confirm="确认开始清理? (Y/N): "
if /i not "%confirm%"=="Y" goto end

echo.
echo ================================================
echo            🧹 正在清理...
echo ================================================

:: 1. Windows 临时文件
echo.
echo [1/6] 清理 Windows 临时文件...
del /q /f "%WINDIR%\Temp\*" 2>nul
del /q /f "%LOCALAPPDATA%\Temp\*" 2>nul

:: 2. 用户缓存
echo [2/6] 清理用户缓存...
del /q /f "%LOCALAPPDATA%\Microsoft\Windows\INetCache\*" 2>nul

:: 3. 浏览器缓存
echo [3/6] 清理浏览器缓存...
del /q /f "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache\*" 2>nul
del /q /f "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache\*" 2>nul

:: 4. Windows 更新缓存
echo [4/6] 清理更新缓存...
net stop wuauserv >nul 2>&1
del /q /f "%WINDIR%\SoftwareDistribution\Download\*" 2>nul
net start wuauserv >nul 2>&1

:: 5. 清理日志
echo [5/6] 清理日志文件...
del /q /f "%WINDIR%\Logs\*.log" 2>nul
del /q /f "%WINDIR%\Panther\*" 2>nul

:: 6. 清理回收站
echo [6/6] 清理回收站...
powershell -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue" 2>nul

echo.
echo ================================================
echo            ✅ 清理完成！
echo ================================================
echo.
echo 已清理：
echo   - 临时文件
echo   - 浏览器缓存
echo   - 更新缓存
echo   - 日志文件
echo   - 回收站
echo.
pause

:end
echo.
echo 已取消清理。
pause
