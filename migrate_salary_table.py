# -*- coding: utf-8 -*-
"""
迁移脚本：创建工资表 (salary)
运行方式：python migrate_salary_table.py
"""

import sqlite3
import os

def migrate():
    # 确保数据库目录存在
    if not os.path.exists('instance'):
        os.makedirs('instance')

    # 连接数据库
    conn = sqlite3.connect('instance/company_data.db')
    cursor = conn.cursor()

    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='salary'")
        if cursor.fetchone():
            print('[SKIP] salary 表已存在')
        else:
            # 创建工资表
            cursor.execute('''
                CREATE TABLE salary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    userid VARCHAR(20) NOT NULL,
                    username VARCHAR(20) NOT NULL,
                    position VARCHAR(50),
                    year_month VARCHAR(7) NOT NULL,
                    work_days INTEGER DEFAULT 0,
                    month_days INTEGER DEFAULT 26,
                    base_salary FLOAT DEFAULT 0,
                    base_salary_rate FLOAT DEFAULT 0,
                    pre_sales FLOAT DEFAULT 0,
                    pre_sales_rate FLOAT DEFAULT 0.03,
                    pre_sales_commission FLOAT DEFAULT 0,
                    post_sales FLOAT DEFAULT 0,
                    post_sales_rate FLOAT DEFAULT 0.05,
                    post_sales_commission FLOAT DEFAULT 0,
                    referral_count INTEGER DEFAULT 0,
                    referral_commission FLOAT DEFAULT 0,
                    makeup_count INTEGER DEFAULT 0,
                    makeup_commission FLOAT DEFAULT 0,
                    dress_count INTEGER DEFAULT 0,
                    dress_commission FLOAT DEFAULT 0,
                    full_day_bonus FLOAT DEFAULT 0,
                    social_subsidy FLOAT DEFAULT 0,
                    housing_subsidy FLOAT DEFAULT 0,
                    full_attendance_bonus FLOAT DEFAULT 0,
                    other_subsidy FLOAT DEFAULT 0,
                    total_salary FLOAT DEFAULT 0,
                    social_deduction FLOAT DEFAULT 0,
                    other_deduction FLOAT DEFAULT 0,
                    actual_salary FLOAT DEFAULT 0,
                    remark VARCHAR(300),
                    created_by VARCHAR(20),
                    created_time DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print('[OK] 创建 salary 表成功')

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
