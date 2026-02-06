#!/usr/bin/env python
"""
测试 MySQL 连接
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection(password=None):
    """测试MySQL连接"""
    try:
        db = pymysql.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER', 'root'),
            password=password or os.getenv('DB_PASSWORD', ''),
            port=int(os.getenv('DB_PORT', 3306)),
            connect_timeout=5
        )
        cursor = db.cursor()
        cursor.execute('SELECT VERSION()')
        version = cursor.fetchone()[0]
        print(f"✅ 连接成功！MySQL版本: {version}")
        db.close()
        return True
    except pymysql.err.OperationalError as e:
        print(f"❌ 连接失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("测试 MySQL 连接")
    print("="*60)
    
    # 先测试当前配置的密码
    print("\n1. 测试当前配置的密码...")
    if test_connection():
        print("\n✅ 密码正确，可以继续初始化！")
        exit(0)
    
    # 测试无密码
    print("\n2. 测试无密码连接...")
    if test_connection(''):
        print("\n✅ 无密码连接成功！")
        print("请更新 .env 文件中的 DB_PASSWORD 为空")
        exit(0)
    
    # 让用户输入密码
    print("\n3. 请手动输入密码测试...")
    print("（如果密码错误，请检查 .env 文件）")
    print("\n提示：可以通过命令行参数传入密码测试：")
    print("  python3 test_mysql_connection.py <密码>")
    
    import sys
    if len(sys.argv) > 1:
        password = sys.argv[1]
        if test_connection(password):
            print(f"\n✅ 密码正确！")
            print(f"\n请更新 .env 文件，设置: DB_PASSWORD={password}")
            exit(0)
    else:
        print("\n请运行: python3 test_mysql_connection.py <你的密码>")
    
    print("\n❌ 所有尝试都失败了，请检查：")
    print("  1. MySQL 服务是否正在运行")
    print("  2. 端口是否正确（默认3306）")
    print("  3. root 用户密码是否正确")
    print("  4. root 用户是否有远程连接权限")
