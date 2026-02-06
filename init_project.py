#!/usr/bin/env python
"""
项目初始化脚本
用于一键设置数据库、创建超级用户和测试数据
"""
import os
import sys
import subprocess
from pathlib import Path

def print_step(step_num, description):
    """打印步骤信息"""
    print(f"\n{'='*60}")
    print(f"步骤 {step_num}: {description}")
    print('='*60)

def check_env_file():
    """检查 .env 文件是否存在"""
    env_path = Path('.env')
    if env_path.exists():
        print("✓ .env 文件已存在")
        return True
    else:
        print("✗ .env 文件不存在")
        return False

def create_env_file():
    """创建 .env 文件"""
    print("\n正在创建 .env 文件...")
    
    # 读取示例文件
    example_path = Path('.env.example')
    if example_path.exists():
        with open(example_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        # 如果示例文件不存在，创建默认内容
        content = """# Django 配置
DJANGO_SECRET_KEY=django-insecure-change-me-later

# MySQL 数据库配置
DB_NAME=aisec_db
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
"""
    
    # 获取用户输入
    print("\n请输入数据库配置信息（直接回车使用默认值）：")
    db_name = input("数据库名称 [aisec_db]: ").strip() or "aisec_db"
    db_user = input("数据库用户名 [root]: ").strip() or "root"
    db_password = input("数据库密码 []: ").strip() or ""
    db_host = input("数据库主机 [127.0.0.1]: ").strip() or "127.0.0.1"
    db_port = input("数据库端口 [3306]: ").strip() or "3306"
    
    # 替换配置
    content = content.replace('DB_NAME=aisec_db', f'DB_NAME={db_name}')
    content = content.replace('DB_USER=root', f'DB_USER={db_user}')
    content = content.replace('DB_PASSWORD=', f'DB_PASSWORD={db_password}')
    content = content.replace('DB_HOST=127.0.0.1', f'DB_HOST={db_host}')
    content = content.replace('DB_PORT=3306', f'DB_PORT={db_port}')
    
    # 写入 .env 文件
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ .env 文件创建成功")

def create_database():
    """创建数据库"""
    print("\n正在创建数据库...")
    try:
        result = subprocess.run([sys.executable, 'create_db.py'], 
                              capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        if result.returncode != 0:
            print(f"错误: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"创建数据库时出错: {e}")
        return False

def run_migrations():
    """运行数据库迁移"""
    print("\n正在运行数据库迁移...")
    try:
        result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                              capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        if result.returncode != 0:
            print(f"错误: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"运行迁移时出错: {e}")
        return False

def create_superuser():
    """创建超级用户"""
    print("\n正在创建超级用户...")
    try:
        result = subprocess.run([sys.executable, 'create_superuser.py'], 
                              capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        if result.returncode != 0:
            print(f"错误: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"创建超级用户时出错: {e}")
        return False

def create_dummy_data():
    """创建测试数据"""
    print("\n是否创建测试数据？(y/n) [y]: ", end='')
    choice = input().strip().lower() or 'y'
    if choice == 'y':
        try:
            result = subprocess.run([sys.executable, 'create_dummy_data.py'], 
                                  capture_output=True, text=True, encoding='utf-8')
            print(result.stdout)
            if result.returncode != 0:
                print(f"错误: {result.stderr}")
                return False
            return True
        except Exception as e:
            print(f"创建测试数据时出错: {e}")
            return False
    else:
        print("跳过创建测试数据")
        return True

def main():
    """主函数"""
    print("\n" + "="*60)
    print("AI安全靶场 - 项目初始化脚本")
    print("="*60)
    
    # 步骤1: 检查并创建 .env 文件
    print_step(1, "配置环境变量")
    if not check_env_file():
        create_env_file()
    else:
        print("\n.env 文件已存在，是否重新配置？(y/n) [n]: ", end='')
        if input().strip().lower() == 'y':
            create_env_file()
    
    # 步骤2: 创建数据库
    print_step(2, "创建数据库")
    if not create_database():
        print("\n❌ 数据库创建失败，请检查 MySQL 服务是否运行")
        print("   提示: 确保 MySQL 已安装并运行，且配置的用户有创建数据库的权限")
        return
    
    # 步骤3: 运行迁移
    print_step(3, "运行数据库迁移")
    if not run_migrations():
        print("\n❌ 数据库迁移失败")
        return
    
    # 步骤4: 创建超级用户
    print_step(4, "创建超级用户")
    if not create_superuser():
        print("\n❌ 超级用户创建失败")
        return
    
    # 步骤5: 创建测试数据（可选）
    print_step(5, "创建测试数据（可选）")
    create_dummy_data()
    
    # 完成
    print("\n" + "="*60)
    print("✅ 项目初始化完成！")
    print("="*60)
    print("\n登录信息：")
    print("  用户名: admin")
    print("  密码: admin")
    print("\n启动服务器：")
    print("  python manage.py runserver")
    print("\n然后访问: http://127.0.0.1:8000")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n初始化已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)
