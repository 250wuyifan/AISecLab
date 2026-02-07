#!/bin/bash
#
# AI 安全靶场 - Linux/macOS 启动脚本
#

echo ""
echo "🛡️  AI 安全靶场 启动中..."
echo ""

# 检测 Python
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ 未找到 Python"
    exit 1
fi

# 检查数据库是否已初始化
if [ ! -f "db.sqlite3" ]; then
    echo "⚠️  数据库未初始化，正在初始化..."
    $PYTHON manage.py migrate --noinput
    $PYTHON create_superuser.py
fi

echo "🚀 启动 Django 服务..."
echo "📍 访问地址: http://127.0.0.1:8000"
echo "🔑 登录账号: admin / admin"
echo "----------------------------------------"
echo "按 Ctrl+C 停止服务"
echo ""

$PYTHON manage.py runserver
