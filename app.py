# app.py

from flask import Flask, render_template, request, redirect, session, url_for, flash,jsonify
from database import db, Order, User
from sqlalchemy import desc
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 配置 SQLite 数据库的连接地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///company_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库连接
db.init_app(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']

        # 在这里进行用户验证，检查userid和密码是否匹配
        user = User.query.filter_by(userid=userid).first()

        if user and user.password == password:
            # 用户验证成功
            session['userid'] = userid
            return redirect(url_for('index'))
        else:
            # 用户验证失败，返回错误信息
            return render_template('login.html', error='用户ID或密码错误！')

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
        wedding_dress_price = request.form['wedding_dress_price']
        photography_price = request.form['photography_price']
        videography_price = request.form['videography_price']
        makeup_price = request.form['makeup_price']
        dress_rental_price = request.form['dress_rental_price']
        wedding_celebration_price = request.form['wedding_celebration_price']
        total_price = request.form['total_price']
        order_time_str= request.form['order_time']
        # 字符串日期转换成日期格式
        order_time = datetime.strptime(order_time_str, '%Y-%m-%d')
        choosePicture_time_str = request.form['choosePicture_time']
        choosePicture_time = datetime.strptime(choosePicture_time_str, '%Y-%m-%d')
        confirmPicture_time_str = request.form['confirmPicture_time']
        confirmPicture_time = datetime.strptime(confirmPicture_time_str, '%Y-%m-%d')
        order_status = request.form['order_status']
        shoot_time_str = request.form['shoot_time']
        shoot_time = datetime.strptime(shoot_time_str, '%Y-%m-%d')
        sales_consultant = request.form['sales_consultant']
        photographer = request.form['photographer']
        makeup_artist = request.form['makeup_artist']

        # 检查价格字段是否为空，如果为空，则设置为0
        wedding_dress_price = float(wedding_dress_price) if wedding_dress_price else 0.0
        photography_price = float(photography_price) if photography_price else 0.0
        makeup_price = float(makeup_price) if makeup_price else 0.0
        dress_rental_price = float(dress_rental_price) if dress_rental_price else 0.0
        wedding_celebration_price = float(wedding_celebration_price) if wedding_celebration_price else 0.0
        total_price = float(total_price) if total_price else 0.0
        videography_price = float(videography_price) if videography_price else 0.0
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
            created_by=session['userid']  # 添加创建人的字段
        )
        try:
            db.session.add(new_order)
            print(new_order)
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
                'message': '订单添加失败: ' + str(e)
            }
            return jsonify(response_data), 500


        # 添加编辑页面的路由
@app.route('/edit_order/<int:order_id>', methods=['GET'])
def edit_order_page(order_id):
    if 'userid' in session:
        # 查询数据库中是否存在指定ID的订单
        order = Order.query.get(order_id)

        if order:
            return render_template('edit_order.html', order=order)
        else:
            flash('订单不存在或已被删除！', 'error')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    # 登出，清除用户登录状态
    session.pop('userid', None)
    return redirect(url_for('login'))

# 订单首页
@app.route('/')
def index():
    if 'userid' in session:
        # 获取当前页码参数
        page = request.args.get('page', 1, type=int)
        # 每页显示的订单数量
        per_page = 10
        # 查询订单数据，并按照创建时间倒序排序
        orders = Order.query.order_by(desc(Order.created_time)).paginate(page=page, per_page=per_page)
        return render_template('index.html', orders=orders)
    else:
        return redirect(url_for('login'))


@app.route('/delete_order/<int:order_id>', methods=['GET'])
def delete_order(order_id):
    if 'userid' in session:
        # 查询数据库中是否存在指定ID的订单
        order = Order.query.get(order_id)

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


# 创建处理编辑请求的路由
@app.route('/edit_order/<int:order_id>', methods=['POST'])
def edit_order(order_id):
    if 'userid' in session:
        # 查询数据库中是否存在指定ID的订单
        order = Order.query.get(order_id)

        if order:
            # 更新订单信息
            order.groom_name = request.form['groom_name']
            order.bride_name = request.form['bride_name']
            order.groom_phone = request.form['groom_phone']
            order.bride_phone = request.form['bride_phone']
            order.wedding_dress_price = request.form['wedding_dress_price']
            order.photography_price = request.form['photography_price']
            order.videography_price = request.form['videography_price']
            order.makeup_price = request.form['makeup_price']
            order.dress_rental_price = request.form['dress_rental_price']
            order.wedding_celebration_price = request.form['wedding_celebration_price']
            order.total_price = request.form['total_price']
            order.order_time = request.form['order_time']
            order.shoot_time = request.form['shoot_time']
            order.sales_consultant = request.form['sales_consultant']
            order.photographer = request.form['photographer']
            order.makeup_artist = request.form['makeup_artist']

            # 提交更改到数据库
            db.session.commit()
            flash('订单修改成功！', 'success')
        else:
            flash('订单不存在或已被删除！', 'error')

    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', port=5000, debug=True)

