@echo off
chcp 65001 >nul
title AI 安全靶场 - 安装脚本

echo.
echo ============================================================
echo   🛡️  AI 安全靶场 - Windows 一键安装
echo ============================================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python 3.9+
    echo    下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] 检查 Python 版本...
python --version

echo.
echo [2/5] 检查虚拟环境...
if exist "venv" (
    echo ✓ 虚拟环境已存在
) else (
    echo 未检测到虚拟环境，建议创建虚拟环境运行
    set /p choice="是否创建虚拟环境? [y/N]: "
    if /i "%choice%"=="y" (
        echo 创建虚拟环境...
        python -m venv venv
        echo.
        echo ⚠️  请运行以下命令激活虚拟环境后重新运行此脚本:
        echo    .\venv\Scripts\activate
        pause
        exit /b 0
    )
)

echo.
echo [3/5] 安装 Python 依赖...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [4/5] 初始化数据库...
python manage.py migrate --noinput

echo.
echo [5/5] 创建管理员账号...
python create_superuser.py

echo.
echo ============================================================
echo   🎉 安装完成！
echo ============================================================
echo.
echo   启动服务：python manage.py runserver
echo   访问地址：http://127.0.0.1:8000
echo   登录账号：admin / admin
echo.
echo ============================================================
echo.
pause
