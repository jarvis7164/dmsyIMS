# -*- coding: utf-8 -*-
# 数据库迁移脚本 - 创建客资表

from app import app, db
from database import CustomerLead

with app.app_context():
    # 创建所有不存在的表
    db.create_all()
    print("数据库表已更新")
    print("CustomerLead 表已创建（如果不存在）")
