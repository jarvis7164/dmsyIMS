# -*- coding: utf-8 -*-
"""
迁移脚本：为 user 表添加新增的薪资字段
运行方式：python migrate_user_salary_fields.py
"""

import sqlite3

def migrate():
    # 连接数据库
    conn = sqlite3.connect('instance/company_data.db')
    cursor = conn.cursor()

    try:
        # 检查字段是否存在
        cursor.execute("PRAGMA table_info(user)")
        columns = [row[1] for row in cursor.fetchall()]

        # 添加总提点字段
        if 'total_rate' not in columns:
            cursor.execute('ALTER TABLE user ADD COLUMN total_rate FLOAT DEFAULT 0')
            print('[OK] 添加 total_rate 字段成功')
        else:
            print('[SKIP] total_rate 字段已存在')

        # 添加基本薪资字段
        if 'base_salary' not in columns:
            cursor.execute('ALTER TABLE user ADD COLUMN base_salary FLOAT DEFAULT 0')
            print('[OK] 添加 base_salary 字段成功')
        else:
            print('[SKIP] base_salary 字段已存在')

        # 添加单张修片价格字段
        if 'photo_price' not in columns:
            cursor.execute('ALTER TABLE user ADD COLUMN photo_price FLOAT DEFAULT 0')
            print('[OK] 添加 photo_price 字段成功')
        else:
            print('[SKIP] photo_price 字段已存在')

        # 添加化妆品补贴字段
        if 'makeup_subsidy' not in columns:
            cursor.execute('ALTER TABLE user ADD COLUMN makeup_subsidy FLOAT DEFAULT 0')
            print('[OK] 添加 makeup_subsidy 字段成功')
        else:
            print('[SKIP] makeup_subsidy 字段已存在')

        # 添加耗材补贴字段
        if 'material_subsidy' not in columns:
            cursor.execute('ALTER TABLE user ADD COLUMN material_subsidy FLOAT DEFAULT 0')
            print('[OK] 添加 material_subsidy 字段成功')
        else:
            print('[SKIP] material_subsidy 字段已存在')

        # 添加其他补贴字段
        if 'other_subsidy' not in columns:
            cursor.execute('ALTER TABLE user ADD COLUMN other_subsidy FLOAT DEFAULT 0')
            print('[OK] 添加 other_subsidy 字段成功')
        else:
            print('[SKIP] other_subsidy 字段已存在')

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
