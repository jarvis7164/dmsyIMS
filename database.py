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
    __tablename__ = 'order'
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
    extra_film_price = db.Column(db.Float)  # 加片金额
    total_price = db.Column(db.Float)  # 总价格
    order_time = db.Column(db.DateTime)  # 订单时间
    shoot_time = db.Column(db.DateTime)  # 拍摄时间
    choosePicture_time = db.Column(db.DateTime)  # 选片时间
    confirmPicture_time = db.Column(db.DateTime)  # 看精修时间
    order_status = db.Column(db.String(20))  # 订单状态
    sales_consultant = db.Column(db.String(20))
    photographer = db.Column(db.String(20))
    makeup_artist = db.Column(db.String(20))
    remark = db.Column(db.String(300))  # 备注
    created_by = db.Column(db.String(20))  # 订单创建人
    created_time = db.Column(db.DateTime, default=datetime.utcnow().replace(microsecond=0))  # 订单创建时间


# 员工信息表
class User(db.Model):
    __tablename__ = 'user'
    userid = db.Column(db.String(20), primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(256), nullable=False)  # 增加长度以存储哈希密码
    position = db.Column(db.String(50))  # 岗位
    phone = db.Column(db.String(16))
    address = db.Column(db.String(100))  # 地址
    basic_salary = db.Column(db.Float)  # 底薪
    total_rate = db.Column(db.Float)  # 总提点
    pre_sales_rate = db.Column(db.Float)  # 前期提点率
    post_sales_rate = db.Column(db.Float)  # 后期提点率
    base_salary = db.Column(db.Float)  # 基本薪资
    guaranteed_salary = db.Column(db.Float)  # 保底薪资
    photo_price = db.Column(db.Float)  # 单张修片价格
    makeup_subsidy = db.Column(db.Float)  # 化妆品补贴
    material_subsidy = db.Column(db.Float)  # 耗材补贴
    other_subsidy = db.Column(db.Float)  # 其他补贴
    created_by = db.Column(db.String(20))  # 创建人，默认为 'admin'
    created_time = db.Column(db.DateTime, default=datetime.utcnow().replace(microsecond=0))  # 创建时间，默认为当前时间

    # 用户与角色的多对多关系
    roles = db.relationship('Role', secondary='user_role', backref=db.backref('users', lazy='dynamic'))


# 角色表
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)  # 角色名称
    role_code = db.Column(db.String(50), unique=True, nullable=False)  # 角色编码
    description = db.Column(db.String(200))  # 角色描述
    created_time = db.Column(db.DateTime, default=datetime.utcnow().replace(microsecond=0))

    # 角色与菜单的多对多关系
    menus = db.relationship('Menu', secondary='role_menu', backref=db.backref('roles', lazy='dynamic'))


# 菜单表
class Menu(db.Model):
    __tablename__ = 'menu'
    id = db.Column(db.Integer, primary_key=True)
    menu_name = db.Column(db.String(50), nullable=False)  # 菜单名称
    menu_code = db.Column(db.String(50), unique=True, nullable=False)  # 菜单编码
    menu_url = db.Column(db.String(100))  # 菜单 URL
    parent_id = db.Column(db.Integer, default=0)  # 父菜单 ID，0 表示一级菜单
    icon = db.Column(db.String(50))  # 菜单图标
    sort_order = db.Column(db.Integer, default=0)  # 排序顺序
    is_visible = db.Column(db.Boolean, default=True)  # 是否可见
    created_time = db.Column(db.DateTime, default=datetime.utcnow().replace(microsecond=0))


# 角色 - 菜单关联表
role_menu = db.Table('role_menu',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('menu_id', db.Integer, db.ForeignKey('menu.id'), primary_key=True)
)


# 用户 - 角色关联表
user_role = db.Table('user_role',
    db.Column('user_id', db.String(20), db.ForeignKey('user.userid'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)


# 工资表
class Salary(db.Model):
    __tablename__ = 'salary'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(20), nullable=False)  # 用户 ID
    username = db.Column(db.String(20), nullable=False)  # 姓名
    position = db.Column(db.String(50))  # 岗位
    year_month = db.Column(db.String(7), nullable=False)  # 年月 (格式：2026-01)
    work_days = db.Column(db.Integer, default=0)  # 上班天数
    month_days = db.Column(db.Integer, default=26)  # 当月天数
    base_salary = db.Column(db.Float, default=0)  # 底薪（计算后）
    base_salary_rate = db.Column(db.Float, default=0)  # 底薪基数
    pre_sales = db.Column(db.Float, default=0)  # 前期业绩
    pre_sales_rate = db.Column(db.Float, default=0.03)  # 前期提成率
    pre_sales_commission = db.Column(db.Float, default=0)  # 前期提成
    post_sales = db.Column(db.Float, default=0)  # 后期业绩
    post_sales_rate = db.Column(db.Float, default=0.05)  # 后期提成率
    post_sales_commission = db.Column(db.Float, default=0)  # 后期提成
    referral_count = db.Column(db.Integer, default=0)  # 转介绍人数（化妆师用）
    referral_commission = db.Column(db.Float, default=0)  # 转介绍提成
    makeup_count = db.Column(db.Integer, default=0)  # 化妆品人数（化妆师用）
    makeup_commission = db.Column(db.Float, default=0)  # 化妆品提成
    dress_count = db.Column(db.Integer, default=0)  # 服装人数（化妆师用）
    dress_commission = db.Column(db.Float, default=0)  # 服装提成
    full_day_bonus = db.Column(db.Float, default=0)  # 全天奖
    social_subsidy = db.Column(db.Float, default=0)  # 社保补贴
    housing_subsidy = db.Column(db.Float, default=0)  # 住房补贴
    full_attendance_bonus = db.Column(db.Float, default=0)  # 全勤奖
    other_subsidy = db.Column(db.Float, default=0)  # 其他补贴
    total_salary = db.Column(db.Float, default=0)  # 应发总额
    social_deduction = db.Column(db.Float, default=0)  # 社保扣除
    other_deduction = db.Column(db.Float, default=0)  # 其他扣除
    actual_salary = db.Column(db.Float, default=0)  # 实发工资
    remark = db.Column(db.String(300))  # 备注
    created_by = db.Column(db.String(20))  # 创建人
    created_time = db.Column(db.DateTime, default=datetime.utcnow().replace(microsecond=0))
