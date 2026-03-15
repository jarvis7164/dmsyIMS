# -*- coding: utf-8 -*-
# 用户注册脚本 - 用于创建用户（密码自动哈希）
from flask import Flask
from database import db, User
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///company_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_user():
    print("=== 创建用户 ===")
    userid = input("用户 ID: ")
    username = input("用户名：")
    password = input("密码：")
    position = input("岗位（可选）: ")
    phone = input("电话（可选）: ")

    with app.app_context():
        # 检查用户是否已存在
        existing_user = User.query.filter_by(userid=userid).first()
        if existing_user:
            print(f"错误：用户 {userid} 已存在！")
            return

        # 创建用户，密码自动哈希
        new_user = User(
            userid=userid,
            username=username,
            password=generate_password_hash(password),
            position=position or '',
            phone=phone or '',
            created_by='admin'
        )
        db.session.add(new_user)
        db.session.commit()
        print(f"用户 {username} 创建成功！")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    create_user()
