@echo off
REM Windows 双击启动器
chcp 65001 > nul
cd /d "%~dp0"

REM 检测 Python
where python >nul 2>nul
if %errorlevel% == 0 (
    set PY=python
    goto :run
)
where py >nul 2>nul
if %errorlevel% == 0 (
    set PY=py -3
    goto :run
)

echo.
echo [!] 未检测到 Python 3
echo.
echo 请前往 https://www.python.org/downloads/ 下载安装 Python 3.x
echo 安装时务必勾选 "Add Python to PATH"
echo.
pause
exit /b 1

:run
cls
echo.
echo  正在启动 App Store 全球比价工具...
echo.
%PY% AppPriceTracker.py
pause
