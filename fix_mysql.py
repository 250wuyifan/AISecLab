#!/usr/bin/env python
"""
修复 MySQL 连接问题
"""
import pymysql
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_and_fix():
    """测试并修复MySQL连接"""
    print("="*60)
    print("MySQL 连接诊断工具")
    print("="*60)
    
    host = os.getenv('DB_HOST', '127.0.0.1')
    user = os.getenv('DB_USER', 'root')
    port = int(os.getenv('DB_PORT', 3306))
    
    print(f"\n当前配置：")
    print(f"  主机: {host}")
    print(f"  用户: {user}")
    print(f"  端口: {port}")
    print(f"  密码: {'已设置' if os.getenv('DB_PASSWORD') else '未设置'}")
    
    # 尝试几个常见密码
    common_passwords = ['', '123456', 'root', 'password', '12345678']
    
    if len(sys.argv) > 1:
        common_passwords = [sys.argv[1]] + common_passwords
    
    print(f"\n正在测试连接...")
    
    for password in common_passwords:
        try:
            db = pymysql.connect(
                host=host,
                user=user,
                password=password,
                port=port,
                connect_timeout=5
            )
            cursor = db.cursor()
            cursor.execute('SELECT VERSION()')
            version = cursor.fetchone()[0]
            print(f"\n✅ 连接成功！")
            print(f"  MySQL版本: {version}")
            print(f"  正确密码: {'(空)' if password == '' else password}")
            
            # 更新.env文件
            update_env_file(password)
            
            db.close()
            return True
        except pymysql.err.OperationalError as e:
            if 'Access denied' in str(e):
                continue  # 密码错误，继续尝试下一个
            else:
                print(f"\n❌ 连接错误: {e}")
                return False
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            return False
    
    print(f"\n❌ 所有常见密码都失败了")
    print(f"\n请手动测试密码：")
    print(f"  python3 fix_mysql.py <你的密码>")
    print(f"\n或者检查：")
    print(f"  1. MySQL服务是否运行: brew services list | grep mysql")
    print(f"  2. 端口是否正确")
    print(f"  3. root用户密码")
    
    return False

def update_env_file(password):
    """更新.env文件中的密码"""
    env_path = '.env'
    if not os.path.exists(env_path):
        print("⚠️  .env文件不存在，无法自动更新")
        return
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        updated = False
        with open(env_path, 'w', encoding='utf-8') as f:
            for line in lines:
                if line.startswith('DB_PASSWORD='):
                    f.write(f'DB_PASSWORD={password}\n')
                    updated = True
                else:
                    f.write(line)
            
            if not updated:
                f.write(f'\nDB_PASSWORD={password}\n')
        
        print(f"\n✅ 已更新 .env 文件中的密码")
    except Exception as e:
        print(f"\n⚠️  无法更新.env文件: {e}")
        print(f"请手动设置: DB_PASSWORD={password}")

if __name__ == '__main__':
    test_and_fix()
