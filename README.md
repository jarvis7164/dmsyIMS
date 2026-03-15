# 大麦摄影管理系统 (DMSY IMS)

基于 Flask 的婚纱摄影订单管理系统

## 修复内容

### 已修复的严重问题

1. **缩进错误** - `edit_order_page` 函数被错误地嵌套在 `add_order` 函数内部，导致路由注册失败

2. **密码安全问题** - 密码从明文存储改为使用 Werkzeug 的 `generate_password_hash` 和 `check_password_hash` 进行哈希加密

3. **价格变量重复转换** - `videography_price` 转换位置错误，已移至正确位置

4. **环境变量配置** - `SECRET_KEY` 和数据库 URI 现在可以通过环境变量配置

### 新增功能

1. **输入验证**
   - 电话号码格式验证（中国大陆手机号）
   - 价格字段验证（不能为负数）

2. **辅助脚本**
   - `create_user.py` - 创建新用户（自动哈希密码）
   - `migrate_passwords.py` - 将现有明文密码迁移为哈希密码

3. **错误显示** - 登录页面现在会显示错误信息

## 快速开始

### 1. 安装依赖

```bash
pip install Flask Flask-SQLAlchemy python-dotenv
```

### 2. 配置环境变量（可选）

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，设置你的密钥
```

### 3. 初始化数据库并创建用户

```bash
# 初始化数据库（运行 app.py 会自动创建）
python app.py

# 创建第一个用户（在新终端运行）
python create_user.py
```

### 4. 迁移现有密码（如果是升级）

如果数据库中已有用户，需要运行密码迁移：

```bash
python migrate_passwords.py
```

### 5. 启动应用

```bash
python app.py
```

访问 http://localhost:5000

## 项目结构

```
D:\python\dmsyIMS/
├── app.py                  # 主应用文件
├── database.py             # 数据库模型
├── create_user.py          # 用户创建脚本
├── migrate_passwords.py    # 密码迁移脚本
├── .env.example            # 环境变量示例
├── templates/
│   ├── login.html          # 登录页面
│   ├── index.html          # 订单列表
│   ├── add_order.html      # 添加订单
│   └── edit_order.html     # 编辑订单
└── instance/
    └── company_data.db     # SQLite 数据库（自动生成）
```

## 默认账户

使用 `create_user.py` 脚本创建的第一个用户即为管理员账户。

## 安全建议

1. **生产环境必须修改** `.env` 中的 `SECRET_KEY`
2. **禁用 debug 模式** - 将 `app.run()` 中的 `debug=True` 改为 `False`
3. **使用正式数据库** - 建议从 SQLite 迁移到 MySQL 或 PostgreSQL
4. **启用 HTTPS** - 生产环境应使用 HTTPS

## 待改进功能

- [ ] 添加 CSRF 保护（需要 Flask-WTF）
- [ ] 添加用户角色权限管理
- [ ] 添加数据统计和报表功能
- [ ] 改进前端 UI/UX
