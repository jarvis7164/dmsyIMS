# app.py

import os
import re
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from database import db, Order, User, Role, Menu, user_role, role_menu
from sqlalchemy import desc
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

# 时间格式化辅助函数 - 格式为 YYYY-MM-DD HH:MM
def format_datetime(dt):
    """将 datetime 对象格式化为 'YYYY-MM-DD HH:MM' 字符串"""
    if dt is None:
        return ''
    return dt.strftime('%Y-%m-%d %H:%M')

# 输入验证辅助函数
def validate_phone(phone):
    """验证电话号码格式"""
    if not phone:
        return True  # 允许空值
    pattern = r'^1[3-9]\d{9}$'  # 中国大陆手机号
    return bool(re.match(pattern, phone))

def validate_price(price_str):
    """验证价格字段"""
    if not price_str:
        return True, 0.0
    try:
        price = float(price_str)
        if price < 0:
            return False, None
        return True, price
    except (ValueError, TypeError):
        return False, None

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_change_in_production')

# 配置 SQLite 数据库的连接地址
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///company_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库连接
db.init_app(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']

        # 验证用户
        user = db.session.get(User, userid)

        if user and check_password_hash(user.password, password):
            # 用户验证成功
            session['userid'] = userid
            return redirect(url_for('index'))
        else:
            # 用户验证失败，返回错误信息
            return render_template('login.html', error='用户 ID 或密码错误！')

    return render_template('login.html', error='')


@app.route('/add_order_page', methods=['GET'])
def add_order_page():
    if 'userid' in session:
        return render_template('add_order.html')
    else:
        return redirect(url_for('login'))


@app.route('/add_order', methods=['POST'])
def add_order():
    if 'userid' in session:
        # 获取表单提交的数据
        groom_name = request.form['groom_name']
        bride_name = request.form['bride_name']
        groom_phone = request.form['groom_phone']
        bride_phone = request.form['bride_phone']

        # 验证电话号码
        if not validate_phone(groom_phone):
            return jsonify({'success': False, 'message': '新郎电话格式不正确！'}), 400
        if not validate_phone(bride_phone):
            return jsonify({'success': False, 'message': '新娘电话格式不正确！'}), 400

        wedding_dress_price = request.form['wedding_dress_price']
        photography_price = request.form['photography_price']
        videography_price = request.form['videography_price']
        makeup_price = request.form['makeup_price']
        dress_rental_price = request.form['dress_rental_price']
        wedding_celebration_price = request.form['wedding_celebration_price']
        total_price = request.form['total_price']
        order_time_str = request.form['order_time']

        # 验证价格字段
        valid, wedding_dress_price = validate_price(wedding_dress_price)
        if not valid:
            return jsonify({'success': False, 'message': '婚纱照价格格式错误！'}), 400
        valid, photography_price = validate_price(photography_price)
        if not valid:
            return jsonify({'success': False, 'message': '跟拍价格格式错误！'}), 400
        valid, videography_price = validate_price(videography_price)
        if not valid:
            return jsonify({'success': False, 'message': '摄像价格格式错误！'}), 400
        valid, makeup_price = validate_price(makeup_price)
        if not valid:
            return jsonify({'success': False, 'message': '跟妆价格格式错误！'}), 400
        valid, dress_rental_price = validate_price(dress_rental_price)
        if not valid:
            return jsonify({'success': False, 'message': '租礼服价格格式错误！'}), 400
        valid, wedding_celebration_price = validate_price(wedding_celebration_price)
        if not valid:
            return jsonify({'success': False, 'message': '婚庆价格格式错误！'}), 400
        valid, total_price = validate_price(total_price)
        if not valid:
            return jsonify({'success': False, 'message': '总价格格式错误！'}), 400

        # 字符串日期转换成日期格式
        order_time = datetime.strptime(order_time_str, '%Y-%m-%d')
        choosePicture_time_str = request.form.get('choosePicture_time', '')
        choosePicture_time = datetime.strptime(choosePicture_time_str, '%Y-%m-%d') if choosePicture_time_str else None
        confirmPicture_time_str = request.form.get('confirmPicture_time', '')
        confirmPicture_time = datetime.strptime(confirmPicture_time_str, '%Y-%m-%d') if confirmPicture_time_str else None
        order_status = request.form.get('order_status', '待拍摄')
        shoot_time_str = request.form['shoot_time']
        shoot_time = datetime.strptime(shoot_time_str, '%Y-%m-%d')
        sales_consultant = request.form['sales_consultant']
        photographer = request.form['photographer']
        makeup_artist = request.form['makeup_artist']

        # 创建订单对象并保存到数据库
        new_order = Order(
            groom_name=groom_name,
            bride_name=bride_name,
            groom_phone=groom_phone,
            bride_phone=bride_phone,
            wedding_dress_price=wedding_dress_price,
            photography_price=photography_price,
            videography_price=videography_price,
            makeup_price=makeup_price,
            dress_rental_price=dress_rental_price,
            wedding_celebration_price=wedding_celebration_price,
            total_price=total_price,
            order_time=order_time,
            shoot_time=shoot_time,
            choosePicture_time=choosePicture_time,
            confirmPicture_time=confirmPicture_time,
            order_status=order_status,
            sales_consultant=sales_consultant,
            photographer=photographer,
            makeup_artist=makeup_artist,
            created_by=session['userid']
        )
        try:
            db.session.add(new_order)
            db.session.commit()

            # 添加成功信息到会话中
            response_data = {
                'success': True,
                'message': '订单添加成功！'
            }
            return jsonify(response_data), 200
        except Exception as e:
            db.session.rollback()
            response_data = {
                'success': False,
                'message': '订单添加失败：' + str(e)
            }
            return jsonify(response_data), 500


@app.route('/logout')
def logout():
    # 登出，清除用户登录状态
    session.pop('userid', None)
    return redirect(url_for('login'))


@app.route('/')
def index():
    if 'userid' in session:
        # 获取当前页码参数
        page = request.args.get('page', 1, type=int)
        # 每页显示的订单数量
        per_page = 10
        # 查询订单数据，并按照创建时间倒序排序
        orders = Order.query.order_by(desc(Order.created_time)).paginate(page=page, per_page=per_page)
        return render_template('index.html', orders=orders, format_datetime=format_datetime)
    else:
        return redirect(url_for('login'))


@app.route('/delete_order/<int:order_id>', methods=['GET'])
def delete_order(order_id):
    if 'userid' in session:
        # 查询数据库中是否存在指定 ID 的订单
        order = db.session.get(Order, order_id)

        if order:
            # 存在订单，删除订单并提交到数据库
            db.session.delete(order)
            db.session.commit()

            # 添加成功信息到会话中
            flash('订单删除成功！', 'success')
        else:
            # 订单不存在，添加错误信息到会话中
            flash('订单不存在或已被删除！', 'error')

    return redirect(url_for('index'))


# 更新订单状态
@app.route('/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401

    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'success': False, 'message': '订单不存在！'}), 404

    data = request.get_json()
    new_status = data.get('status')

    if new_status:
        order.order_status = new_status
        db.session.commit()
        return jsonify({'success': True, 'message': '状态更新成功！'})
    else:
        return jsonify({'success': False, 'message': '状态不能为空！'}), 400


# 获取订单数据 API
@app.route('/get_order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401

    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'success': False, 'message': '订单不存在！'}), 404

    order_data = {
        'orderid': order.orderid,
        'groom_name': order.groom_name,
        'bride_name': order.bride_name,
        'groom_phone': order.groom_phone,
        'bride_phone': order.bride_phone,
        'wedding_dress_price': order.wedding_dress_price,
        'photography_price': order.photography_price,
        'videography_price': order.videography_price,
        'makeup_price': order.makeup_price,
        'dress_rental_price': order.dress_rental_price,
        'wedding_celebration_price': order.wedding_celebration_price,
        'total_price': order.total_price,
        'order_time': str(order.order_time) if order.order_time else '',
        'shoot_time': str(order.shoot_time) if order.shoot_time else '',
        'choosePicture_time': str(order.choosePicture_time) if order.choosePicture_time else '',
        'confirmPicture_time': str(order.confirmPicture_time) if order.confirmPicture_time else '',
        'order_status': order.order_status,
        'sales_consultant': order.sales_consultant,
        'photographer': order.photographer,
        'makeup_artist': order.makeup_artist
    }

    return jsonify({'success': True, 'order': order_data})


# 创建处理编辑请求的路由
@app.route('/edit_order/<int:order_id>', methods=['POST'])
def edit_order(order_id):
    if 'userid' in session:
        # 查询数据库中是否存在指定 ID 的订单
        order = db.session.get(Order, order_id)

        if order:
            # 更新订单信息（新人信息和价格字段虽然前端设为 readonly，但后端仍然保留不更新）
            order.order_status = request.form['order_status']
            order.order_time = request.form['order_time']
            order.shoot_time = request.form['shoot_time']
            order.sales_consultant = request.form['sales_consultant']
            order.photographer = request.form['photographer']
            order.makeup_artist = request.form['makeup_artist']

            # 处理选片和精修时间（可选字段）
            choosePicture_time_str = request.form.get('choosePicture_time', '')
            if choosePicture_time_str:
                order.choosePicture_time = choosePicture_time_str
            confirmPicture_time_str = request.form.get('confirmPicture_time', '')
            if confirmPicture_time_str:
                order.confirmPicture_time = confirmPicture_time_str

            # 提交更改到数据库
            db.session.commit()
            flash('订单修改成功！', 'success')
        else:
            flash('订单不存在或已被删除！', 'error')

    return redirect(url_for('index'))


# 用户管理页面
@app.route('/user_management')
def user_management():
    if 'userid' in session:
        # 获取当前页码参数
        page = request.args.get('page', 1, type=int)
        # 每页显示的用户数量
        per_page = 10
        # 查询用户数据，并按照创建时间倒序排序
        users = User.query.order_by(desc(User.created_time)).paginate(page=page, per_page=per_page)
        return render_template('user_management.html', users=users)
    else:
        return redirect(url_for('login'))


# 添加用户页面
@app.route('/add_user_page', methods=['GET'])
def add_user_page():
    if 'userid' in session:
        return render_template('add_user.html')
    else:
        return redirect(url_for('login'))


# 添加用户
@app.route('/add_user', methods=['POST'])
def add_user():
    if 'userid' in session:
        userid = request.form['userid']
        username = request.form['username']
        password = request.form['password']
        position = request.form.get('position', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')

        # 验证并转换数值字段
        try:
            basic_salary = float(request.form.get('basic_salary', 0)) if request.form.get('basic_salary') else 0.0
            pre_sales_rate = float(request.form.get('pre_sales_rate', 0)) if request.form.get('pre_sales_rate') else 0.0
            post_sales_rate = float(request.form.get('post_sales_rate', 0)) if request.form.get('post_sales_rate') else 0.0
            guaranteed_salary = float(request.form.get('guaranteed_salary', 0)) if request.form.get('guaranteed_salary') else 0.0
        except ValueError:
            return jsonify({'success': False, 'message': '薪资字段格式不正确！'}), 400

        # 检查用户 ID 是否已存在
        existing_user = db.session.get(User, userid)
        if existing_user:
            return jsonify({'success': False, 'message': '用户 ID 已存在！'}), 400

        # 创建用户对象并保存到数据库
        new_user = User(
            userid=userid,
            username=username,
            password=generate_password_hash(password),
            position=position,
            phone=phone,
            address=address,
            basic_salary=basic_salary,
            pre_sales_rate=pre_sales_rate,
            post_sales_rate=post_sales_rate,
            guaranteed_salary=guaranteed_salary,
            created_by=session['userid']
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'success': True, 'message': '用户添加成功！'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': '用户添加失败：' + str(e)}), 500

    return jsonify({'success': False, 'message': '未登录！'}), 401


# 删除用户
@app.route('/delete_user/<userid>', methods=['GET'])
def delete_user(userid):
    if 'userid' in session:
        # 不允许删除自己
        if userid == session['userid']:
            flash('不能删除自己！', 'error')
            return redirect(url_for('user_management'))

        user = db.session.get(User, userid)
        if user:
            db.session.delete(user)
            db.session.commit()
            flash('用户删除成功！', 'success')
        else:
            flash('用户不存在！', 'error')

    return redirect(url_for('user_management'))


# 编辑用户页面
@app.route('/edit_user_page/<userid>', methods=['GET'])
def edit_user_page(userid):
    if 'userid' in session:
        user = db.session.get(User, userid)
        if user:
            roles = Role.query.all()  # 获取所有角色
            return render_template('edit_user.html', user=user, roles=roles)
        else:
            flash('用户不存在！', 'error')
            return redirect(url_for('user_management'))
    else:
        return redirect(url_for('login'))


# 获取用户角色
@app.route('/get_user_roles/<userid>', methods=['GET'])
def get_user_roles(userid):
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401

    user = db.session.get(User, userid)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在！'}), 404

    all_roles = Role.query.all()
    user_role_ids = [role.id for role in user.roles]

    roles_data = []
    for role in all_roles:
        roles_data.append({
            'id': role.id,
            'role_name': role.role_name,
            'role_code': role.role_code,
            'description': role.description,
            'is_assigned': role.id in user_role_ids
        })

    return jsonify({'success': True, 'roles': roles_data})


# 编辑用户
@app.route('/edit_user/<userid>', methods=['POST'])
def edit_user(userid):
    if 'userid' in session:
        user = db.session.get(User, userid)
        if user:
            user.username = request.form['username']
            user.position = request.form.get('position', '')
            user.phone = request.form.get('phone', '')
            user.address = request.form.get('address', '')

            # 如果密码不为空，则更新密码
            password = request.form.get('password', '')
            if password:
                user.password = generate_password_hash(password)

            # 验证并转换数值字段
            try:
                user.basic_salary = float(request.form.get('basic_salary', 0)) if request.form.get('basic_salary') else 0.0
                user.pre_sales_rate = float(request.form.get('pre_sales_rate', 0)) if request.form.get('pre_sales_rate') else 0.0
                user.post_sales_rate = float(request.form.get('post_sales_rate', 0)) if request.form.get('post_sales_rate') else 0.0
                user.guaranteed_salary = float(request.form.get('guaranteed_salary', 0)) if request.form.get('guaranteed_salary') else 0.0
            except ValueError:
                flash('薪资字段格式不正确！', 'error')
                return redirect(url_for('edit_user_page', userid=userid))

            db.session.commit()
            flash('用户信息更新成功！', 'success')
        else:
            flash('用户不存在！', 'error')

    return redirect(url_for('user_management'))


    return redirect(url_for('user_management'))


# ==================== 角色和权限管理 ====================

# 初始化菜单和角色
def init_menus_and_roles():
    """初始化系统菜单和超级管理员角色"""
    # 检查是否已存在菜单，避免重复初始化
    if Menu.query.first() is not None:
        # 菜单已存在，修复订单管理的 URL
        order_menu = Menu.query.filter_by(menu_code='ORDER_MANAGEMENT').first()
        if order_menu and order_menu.menu_url == '/index':
            order_menu.menu_url = '/'
            db.session.commit()
        return

    # 定义系统菜单
    menus = [
        {'menu_name': '订单管理', 'menu_code': 'ORDER_MANAGEMENT', 'menu_url': '/', 'parent_id': 0, 'icon': '📋', 'sort_order': 1},
        {'menu_name': '用户管理', 'menu_code': 'USER_MANAGEMENT', 'menu_url': '/user_management', 'parent_id': 0, 'icon': '👥', 'sort_order': 2},
        {'menu_name': '角色管理', 'menu_code': 'ROLE_MANAGEMENT', 'menu_url': '/role_management', 'parent_id': 0, 'icon': '🛡️', 'sort_order': 3},
        {'menu_name': '菜单管理', 'menu_code': 'MENU_MANAGEMENT', 'menu_url': '/menu_management', 'parent_id': 0, 'icon': '📁', 'sort_order': 4},
    ]

    # 添加菜单到数据库
    menu_objects = {}
    for menu_data in menus:
        menu = Menu(**menu_data)
        db.session.add(menu)
        menu_objects[menu_data['menu_code']] = menu

    db.session.commit()

    # 创建超级管理员角色
    admin_role = Role.query.filter_by(role_code='ADMIN').first()
    if not admin_role:
        admin_role = Role(
            role_name='超级管理员',
            role_code='ADMIN',
            description='拥有系统所有权限'
        )
        db.session.add(admin_role)
        db.session.commit()

        # 给超级管理员分配所有菜单权限
        admin_role.menus = list(menu_objects.values())
        db.session.commit()

    # 创建普通用户角色
    user_role = Role.query.filter_by(role_code='USER').first()
    if not user_role:
        user_role = Role(
            role_name='普通用户',
            role_code='USER',
            description='只能查看订单，不能修改'
        )
        db.session.add(user_role)
        db.session.commit()

        # 给普通用户分配部分菜单权限
        user_role.menus = [menu_objects['ORDER_MANAGEMENT']]
        db.session.commit()

    # 确保 admin 用户存在并分配超级管理员角色
    admin_user = db.session.get(User, 'admin')
    if admin_user:
        # 检查是否已有超级管理员角色
        if not any(r.role_code == 'ADMIN' for r in admin_user.roles):
            admin_role = Role.query.filter_by(role_code='ADMIN').first()
            admin_user.roles.append(admin_role)
            db.session.commit()


# 角色管理页面
@app.route('/role_management')
def role_management():
    if 'userid' not in session:
        return redirect(url_for('login'))

    # 检查权限
    if not check_permission('ROLE_MANAGEMENT'):
        flash('没有权限访问此页面！', 'error')
        return redirect(url_for('index'))

    page = request.args.get('page', 1, type=int)
    per_page = 10
    roles = Role.query.order_by(desc(Role.created_time)).paginate(page=page, per_page=per_page)
    return render_template('role_management.html', roles=roles)


# 添加角色
@app.route('/add_role', methods=['POST'])
def add_role():
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401

    data = request.get_json()
    role_name = data.get('role_name')
    role_code = data.get('role_code')
    description = data.get('description', '')

    if not role_name or not role_code:
        return jsonify({'success': False, 'message': '角色名称和编码不能为空！'}), 400

    # 检查角色编码是否已存在
    existing_role = Role.query.filter_by(role_code=role_code).first()
    if existing_role:
        return jsonify({'success': False, 'message': '角色编码已存在！'}), 400

    new_role = Role(
        role_name=role_name,
        role_code=role_code,
        description=description
    )

    try:
        db.session.add(new_role)
        db.session.commit()
        return jsonify({'success': True, 'message': '角色添加成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '添加失败：' + str(e)}), 500


# 获取角色详情
@app.route('/get_role/<int:role_id>', methods=['GET'])
def get_role(role_id):
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401

    role = db.session.get(Role, role_id)
    if not role:
        return jsonify({'success': False, 'message': '角色不存在！'}), 404

    role_data = {
        'id': role.id,
        'role_name': role.role_name,
        'role_code': role.role_code,
        'description': role.description,
        'menu_ids': [menu.id for menu in role.menus]
    }

    return jsonify({'success': True, 'role': role_data})


# 更新角色
@app.route('/update_role/<int:role_id>', methods=['POST'])
def update_role(role_id):
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401

    role = db.session.get(Role, role_id)
    if not role:
        return jsonify({'success': False, 'message': '角色不存在！'}), 404

    data = request.get_json()
    role.role_name = data.get('role_name', role.role_name)
    role.role_code = data.get('role_code', role.role_code)
    role.description = data.get('description', role.description)

    # 更新菜单权限
    menu_ids = data.get('menu_ids', [])
    role.menus = Menu.query.filter(Menu.id.in_(menu_ids)).all() if menu_ids else []

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '角色更新成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '更新失败：' + str(e)}), 500


# 删除角色
@app.route('/delete_role/<int:role_id>', methods=['POST'])
def delete_role(role_id):
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401

    role = db.session.get(Role, role_id)
    if not role:
        return jsonify({'success': False, 'message': '角色不存在！'}), 404

    # 不能删除超级管理员角色
    if role.role_code == 'ADMIN':
        return jsonify({'success': False, 'message': '不能删除超级管理员角色！'}), 400

    try:
        db.session.delete(role)
        db.session.commit()
        return jsonify({'success': True, 'message': '角色删除成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '删除失败：' + str(e)}), 500


# 获取所有菜单（树形结构）
@app.route('/get_menus', methods=['GET'])
def get_menus():
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401

    # 检查是否是 admin 用户
    user = db.session.get(User, session['userid'])
    if user and any(r.role_code == 'ADMIN' for r in user.roles):
        # 管理员获取所有菜单
        menus = Menu.query.order_by(Menu.sort_order).all()
    else:
        # 普通用户获取其角色的菜单
        menus = get_user_menus(session['userid'])

    menu_list = []
    for menu in menus:
        menu_list.append({
            'id': menu.id,
            'menu_name': menu.menu_name,
            'menu_code': menu.menu_code,
            'menu_url': menu.menu_url,
            'parent_id': menu.parent_id,
            'icon': menu.icon,
            'sort_order': menu.sort_order,
            'is_visible': menu.is_visible
        })

    return jsonify({'success': True, 'menus': menu_list})


# 获取用户菜单
def get_user_menus(userid):
    """获取用户有权访问的菜单"""
    user = db.session.get(User, userid)
    if not user:
        return []

    # admin 用户返回所有菜单
    if any(r.role_code == 'ADMIN' for r in user.roles):
        return Menu.query.order_by(Menu.sort_order).all()

    # 获取用户所有角色的菜单（去重）
    menu_ids = set()
    for role in user.roles:
        for menu in role.menus:
            menu_ids.add(menu.id)

    return Menu.query.filter(Menu.id.in_(menu_ids)).order_by(Menu.sort_order).all()


# 检查权限
def check_permission(menu_code):
    """检查用户是否有指定菜单的权限"""
    if 'userid' not in session:
        return False

    user = db.session.get(User, session['userid'])
    if not user:
        return False

    # admin 用户拥有所有权限
    if any(r.role_code == 'ADMIN' for r in user.roles):
        return True

    # 检查用户的角色是否有此菜单权限
    for role in user.roles:
        for menu in role.menus:
            if menu.menu_code == menu_code:
                return True

    return False


# 菜单管理页面
@app.route('/menu_management')
def menu_management():
    if 'userid' not in session:
        return redirect(url_for('login'))

    if not check_permission('MENU_MANAGEMENT'):
        flash('没有权限访问此页面！', 'error')
        return redirect(url_for('index'))

    menus = Menu.query.order_by(Menu.sort_order).all()
    return render_template('menu_management.html', menus=menus)


# 添加菜单
@app.route('/add_menu', methods=['POST'])
def add_menu():
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401

    data = request.get_json()
    menu_name = data.get('menu_name')
    menu_code = data.get('menu_code')
    menu_url = data.get('menu_url', '')
    parent_id = data.get('parent_id', 0)
    icon = data.get('icon', '')
    sort_order = data.get('sort_order', 0)

    if not menu_name or not menu_code:
        return jsonify({'success': False, 'message': '菜单名称和编码不能为空！'}), 400

    new_menu = Menu(
        menu_name=menu_name,
        menu_code=menu_code,
        menu_url=menu_url,
        parent_id=parent_id,
        icon=icon,
        sort_order=sort_order
    )

    try:
        db.session.add(new_menu)
        db.session.commit()
        return jsonify({'success': True, 'message': '菜单添加成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '添加失败：' + str(e)}), 500


# 更新菜单
@app.route('/update_menu/<int:menu_id>', methods=['POST'])
def update_menu(menu_id):
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401

    menu = db.session.get(Menu, menu_id)
    if not menu:
        return jsonify({'success': False, 'message': '菜单不存在！'}), 404

    data = request.get_json()
    menu.menu_name = data.get('menu_name', menu.menu_name)
    menu.menu_code = data.get('menu_code', menu.menu_code)
    menu.menu_url = data.get('menu_url', menu.menu_url)
    menu.parent_id = data.get('parent_id', menu.parent_id)
    menu.icon = data.get('icon', menu.icon)
    menu.sort_order = data.get('sort_order', menu.sort_order)
    menu.is_visible = data.get('is_visible', menu.is_visible)

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '菜单更新成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '更新失败：' + str(e)}), 500


# 删除菜单
@app.route('/delete_menu/<int:menu_id>', methods=['POST'])
def delete_menu(menu_id):
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401

    menu = db.session.get(Menu, menu_id)
    if not menu:
        return jsonify({'success': False, 'message': '菜单不存在！'}), 404

    try:
        db.session.delete(menu)
        db.session.commit()
        return jsonify({'success': True, 'message': '菜单删除成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '删除失败：' + str(e)}), 500


# 给用户分配角色
@app.route('/assign_role', methods=['POST'])
def assign_role():
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401

    data = request.get_json()
    userid = data.get('userid')
    role_ids = data.get('role_ids', [])

    user = db.session.get(User, userid)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在！'}), 404

    # 更新用户角色
    user.roles = Role.query.filter(Role.id.in_(role_ids)).all() if role_ids else []

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '角色分配成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '分配失败：' + str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_menus_and_roles()  # 初始化菜单和角色

    app.run(host='0.0.0.0', port=5000, debug=True)
