# -*- coding: utf-8 -*-
# @Time    : 2023/7/29 15:00
# @Author  : Jarvis
# @Email   : jiamiao12@qq.com
# @File    : database.py
# @Software: PyCharm
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# 订单信息表
class Order(db.Model):
    # 定义您的数据模型
    orderid = db.Column(db.Integer, primary_key=True)
    groom_name = db.Column(db.String(20))
    bride_name = db.Column(db.String(20))
    groom_phone = db.Column(db.String(16))
    bride_phone = db.Column(db.String(16))
    wedding_dress_price = db.Column(db.Float)  # 婚纱照价格
    makeup_price = db.Column(db.Float)  # 跟妆价格
    photography_price = db.Column(db.Float)  # 跟拍价格
    videography_price = db.Column(db.Float)  # 摄像价格
    dress_rental_price = db.Column(db.Float)  # 租礼服价格
    wedding_celebration_price = db.Column(db.Float)  # 婚庆价格
    total_price = db.Column(db.Float)  # 总价格
    order_time = db.Column(db.DateTime)  # 订单时间
    shoot_time = db.Column(db.DateTime)  # 拍摄时间
    choosePicture_time = db.Column(db.DateTime)  # 选片时间
    confirmPicture_time = db.Column(db.DateTime)  # 看精修时间
    order_status = db.Column(db.String(20))  # 订单状态
    sales_consultant = db.Column(db.String(20))
    photographer = db.Column(db.String(20))
    makeup_artist = db.Column(db.String(20))
    created_by = db.Column(db.String(20))  # 订单创建人
    created_time = db.Column(db.DateTime, default=datetime.utcnow().replace(microsecond=0))  # 订单创建时间


# 员工信息表
class User(db.Model):
    userid = db.Column(db.String(20), primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    position = db.Column(db.String(50))  # 岗位
    phone = db.Column(db.String(16))
    address = db.Column(db.String(100))  # 地址
    basic_salary = db.Column(db.Float)  # 底薪
    pre_sales_rate = db.Column(db.Float)  # 前期提点率
    post_sales_rate = db.Column(db.Float)  # 后期提点率
    guaranteed_salary = db.Column(db.Float)  # 保底薪资
    created_by = db.Column(db.String(20))  # 创建人，默认为 'admin'
    created_time = db.Column(db.DateTime, default=datetime.utcnow().replace(microsecond=0))  # 创建时间，默认为当前时间
