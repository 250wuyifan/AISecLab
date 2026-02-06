#!/usr/bin/env python3
"""
把当前项目 MySQL 数据库/表统一转换为 utf8mb4，解决 emoji / 中文写入报错：
DataError (1366) Incorrect string value ...
"""

import os
import pymysql
from dotenv import load_dotenv


def main():
    load_dotenv()
    host = os.getenv("DB_HOST", "127.0.0.1")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    port = int(os.getenv("DB_PORT", "3306"))
    db_name = os.getenv("DB_NAME", "aisec_db")

    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        charset="utf8mb4",
        autocommit=True,
    )

    with conn.cursor() as cur:
        print(f"==> ALTER DATABASE `{db_name}` ...")
        cur.execute(f"ALTER DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

        cur.execute(
            "SELECT TABLE_NAME FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA=%s AND TABLE_TYPE='BASE TABLE'",
            (db_name,),
        )
        tables = [r[0] for r in cur.fetchall()]
        print(f"==> found {len(tables)} tables")

        for t in tables:
            print(f"==> CONVERT TABLE `{t}` ...")
            cur.execute(
                f"ALTER TABLE `{db_name}`.`{t}` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )

    conn.close()
    print("✅ 完成：数据库/表已统一为 utf8mb4_unicode_ci")
    print("接下来重启 Django（runserver）后再试创建/上传含 emoji 的 md。")


if __name__ == "__main__":
    main()

