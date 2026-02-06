#!/usr/bin/env python
"""
切换到 SQLite 数据库（开发环境推荐）
SQLite 不需要配置，开箱即用
"""
import os
from pathlib import Path

def switch_to_sqlite():
    """修改 settings.py 使用 SQLite"""
    settings_path = Path('aisec_playground/settings.py')
    
    if not settings_path.exists():
        print("❌ 找不到 settings.py 文件")
        return False
    
    # 读取当前配置
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # SQLite 配置
    sqlite_config = '''DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}'''
    
    # 查找并替换数据库配置
    import re
    pattern = r'DATABASES\s*=\s*\{[^}]+\}'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, sqlite_config, content, flags=re.DOTALL)
        print("✓ 已替换数据库配置为 SQLite")
    else:
        print("⚠️  未找到 DATABASES 配置，请手动检查")
        return False
    
    # 写回文件
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已成功切换到 SQLite 数据库")
    print("\n现在可以运行：")
    print("  python manage.py migrate")
    print("  python create_superuser.py")
    print("  python manage.py runserver")
    
    return True

if __name__ == '__main__':
    print("="*60)
    print("切换到 SQLite 数据库")
    print("="*60)
    print("\nSQLite 优点：")
    print("  ✓ 无需配置 MySQL")
    print("  ✓ 无需密码")
    print("  ✓ 数据库文件存储在项目目录")
    print("  ✓ 适合开发和测试")
    print("\n" + "="*60 + "\n")
    
    switch_to_sqlite()
