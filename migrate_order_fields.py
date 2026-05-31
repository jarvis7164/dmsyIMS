# -*- coding: utf-8 -*-
"""
迁移脚本：为 order 表添加 extra_film_price 和 remark 字段
运行方式：python migrate_order_fields.py
"""

import sqlite3
from database import db, Order

def migrate():
    # 连接数据库
    conn = sqlite3.connect('instance/company_data.db')
    cursor = conn.cursor()

    try:
        # 检查字段是否存在
        cursor.execute("PRAGMA table_info(\"order\")")
        columns = [row[1] for row in cursor.fetchall()]

        # 添加 extra_film_price 字段
        if 'extra_film_price' not in columns:
            cursor.execute('ALTER TABLE "order" ADD COLUMN extra_film_price FLOAT DEFAULT 0')
            print('[OK] 添加 extra_film_price 字段成功')
        else:
            print('[SKIP] extra_film_price 字段已存在')

        # 添加 remark 字段
        if 'remark' not in columns:
            cursor.execute('ALTER TABLE "order" ADD COLUMN remark VARCHAR(300) DEFAULT ""')
            print('[OK] 添加 remark 字段成功')
        else:
            print('[SKIP] remark 字段已存在')

        conn.commit()
        print('\n迁移完成！')

    except Exception as e:
        conn.rollback()
        print(f'迁移失败：{e}')
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
