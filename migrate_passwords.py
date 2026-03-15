# -*- coding: utf-8 -*-
# 密码迁移脚本 - 将现有明文密码转换为哈希密码
# 运行方式：python migrate_passwords.py
from flask import Flask
from database import db, User
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///company_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def migrate_passwords():
    """将明文密码迁移为哈希密码"""
    with app.app_context():
        users = User.query.all()
        migrated_count = 0

        for user in users:
            # 检查密码是否已经是哈希格式（哈希密码通常以 pbkdf2 开头）
            if not user.password.startswith('pbkdf2:'):
                # 这是明文密码，进行哈希
                original_password = user.password
                user.password = generate_password_hash(original_password)
                migrated_count += 1
                print(f"已迁移用户：{user.username} ({user.userid})")

        if migrated_count > 0:
            db.session.commit()
            print(f"\n迁移完成！共迁移 {migrated_count} 个用户。")
        else:
            print("\n没有需要迁移的用户。")

if __name__ == '__main__':
    migrate_passwords()
