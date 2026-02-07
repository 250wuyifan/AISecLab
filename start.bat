@echo off
chcp 65001 >nul
title AI 安全靶场

echo.
echo 🛡️  AI 安全靶场 启动中...
echo.

:: 检查数据库是否已初始化
if not exist "db.sqlite3" (
    echo ⚠️  数据库未初始化，正在初始化...
    python manage.py migrate --noinput
    python create_superuser.py
)

echo 🚀 启动 Django 服务...
echo 📍 访问地址: http://127.0.0.1:8000
echo 🔑 登录账号: admin / admin
echo ----------------------------------------
echo 按 Ctrl+C 停止服务
echo.

python manage.py runserver
