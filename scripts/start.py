#!/usr/bin/env python3
"""
跨平台启动脚本
支持 Windows / macOS / Linux
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def main():
    # 切换到项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print("\n🛡️  AI 安全靶场 启动中...")
    print(f"📁 项目目录: {project_root}")
    print(f"🖥️  系统: {platform.system()}")
    print("-" * 40)
    
    # 检查数据库是否已初始化
    db_path = project_root / "db.sqlite3"
    if not db_path.exists():
        print("⚠️  数据库未初始化，正在初始化...")
        subprocess.run([sys.executable, "manage.py", "migrate", "--noinput"])
        subprocess.run([sys.executable, "create_superuser.py"])
    
    # 启动服务
    print("\n🚀 启动 Django 服务...")
    print("📍 访问地址: http://127.0.0.1:8000")
    print("🔑 登录账号: admin / admin")
    print("-" * 40)
    print("按 Ctrl+C 停止服务\n")
    
    try:
        subprocess.run([sys.executable, "manage.py", "runserver"])
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")

if __name__ == "__main__":
    main()
