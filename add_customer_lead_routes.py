# 客资管理路由 - 临时文件，将被合并到 app.py

# 客资管理页面
@app.route('/customer_lead_management')
def customer_lead_management():
    if 'userid' not in session:
        return redirect(url_for('login'))
    
    # 检查权限
    if not check_permission('CUSTOMER_LEAD_MANAGEMENT'):
        flash('权限不足，请联系管理员！', 'danger')
        return redirect(url_for('index'))
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = 10
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    sales_filter = request.args.get('sales', '')
    
    # 构建查询
    query = CustomerLead.query
    
    # 时间筛选（按创建时间）
    if start_date:
        query = query.filter(db.func.date(CustomerLead.created_time) >= start_date)
    if end_date:
        query = query.filter(db.func.date(CustomerLead.created_time) <= end_date)
    
    # 销售人员筛选
    if sales_filter:
        query = query.filter(CustomerLead.assigned_sales == sales_filter)
    
    # 按创建时间倒序
    query = query.order_by(CustomerLead.created_time.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    leads = pagination.items
    
    # 获取所有销售人员（用于筛选下拉框和分配）
    sales_staff = User.query.filter(User.position == '销售顾问').all()
    
    return render_template('customer_lead_management.html', 
                         leads=leads, 
                         pagination=pagination,
                         start_date=start_date,
                         end_date=end_date,
                         sales_filter=sales_filter,
                         sales_staff=sales_staff,
                         format_datetime=format_datetime)


# 添加客资 API
@app.route('/api/add_customer_lead', methods=['POST'])
def api_add_customer_lead():
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    # 检查权限
    if not check_permission('CUSTOMER_LEAD_MANAGEMENT'):
        return jsonify({'success': False, 'message': '权限不足！'}), 403
    
    data = request.get_json()
    customer_name = data.get('customer_name', '').strip()
    phone = data.get('phone', '').strip()
    assigned_sales = data.get('assigned_sales', '').strip()
    remark = data.get('remark', '').strip()
    
    # 验证必填字段
    if not customer_name:
        return jsonify({'success': False, 'message': '客户姓名不能为空！'}), 400
    
    # 验证电话格式（如果提供）
    if phone and not validate_phone(phone):
        return jsonify({'success': False, 'message': '电话格式不正确！'}), 400
    
    # 确定状态
    if assigned_sales:
        status = '跟踪中'
    else:
        status = '待跟踪'
    
    # 创建客资记录
    new_lead = CustomerLead(
        customer_name=customer_name,
        phone=phone if phone else None,
        assigned_sales=assigned_sales if assigned_sales else None,
        status=status,
        remark=remark[:300] if remark else None,
        created_by=session['userid']
    )
    
    try:
        db.session.add(new_lead)
        db.session.commit()
        return jsonify({'success': True, 'message': '客资添加成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败：{str(e)}'}), 500


# 获取客资详情 API
@app.route('/api/get_customer_lead/<int:lead_id>', methods=['GET'])
def api_get_customer_lead(lead_id):
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    # 检查权限
    if not check_permission('CUSTOMER_LEAD_MANAGEMENT'):
        return jsonify({'success': False, 'message': '权限不足！'}), 403
    
    lead = db.session.get(CustomerLead, lead_id)
    if not lead:
        return jsonify({'success': False, 'message': '客资记录不存在！'}), 404
    
    lead_data = {
        'id': lead.id,
        'customer_name': lead.customer_name,
        'phone': lead.phone or '',
        'assigned_sales': lead.assigned_sales or '',
        'status': lead.status,
        'remark': lead.remark or '',
        'created_by': lead.created_by,
        'created_time': format_datetime(lead.created_time),
        'updated_time': format_datetime(lead.updated_time)
    }
    
    return jsonify({'success': True, 'lead': lead_data})


# 编辑客资 API
@app.route('/api/edit_customer_lead/<int:lead_id>', methods=['POST'])
def api_edit_customer_lead(lead_id):
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    # 检查权限
    if not check_permission('CUSTOMER_LEAD_MANAGEMENT'):
        return jsonify({'success': False, 'message': '权限不足！'}), 403
    
    lead = db.session.get(CustomerLead, lead_id)
    if not lead:
        return jsonify({'success': False, 'message': '客资记录不存在！'}), 404
    
    data = request.get_json()
    customer_name = data.get('customer_name', '').strip()
    phone = data.get('phone', '').strip()
    assigned_sales = data.get('assigned_sales', '').strip()
    status = data.get('status', '').strip()
    remark = data.get('remark', '').strip()
    
    # 验证必填字段
    if not customer_name:
        return jsonify({'success': False, 'message': '客户姓名不能为空！'}), 400
    
    # 验证电话格式（如果提供）
    if phone and not validate_phone(phone):
        return jsonify({'success': False, 'message': '电话格式不正确！'}), 400
    
    # 验证状态
    valid_statuses = ['待跟踪', '跟踪中', '大麦已定', '别家已定', '无效客资']
    if status and status not in valid_statuses:
        return jsonify({'success': False, 'message': '无效的状态值！'}), 400
    
    # 更新客资记录
    lead.customer_name = customer_name
    lead.phone = phone if phone else None
    lead.assigned_sales = assigned_sales if assigned_sales else None
    lead.remark = remark[:300] if remark else None
    
    # 如果提供了状态，使用提供的状态；否则根据销售人员自动设置
    if status:
        lead.status = status
    else:
        # 自动设置状态
        if lead.assigned_sales:
            if lead.status == '待跟踪':
                lead.status = '跟踪中'
        else:
            lead.status = '待跟踪'
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '客资更新成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败：{str(e)}'}), 500


# 删除客资 API
@app.route('/api/delete_customer_lead/<int:lead_id>', methods=['POST'])
def api_delete_customer_lead(lead_id):
    if 'userid' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    # 检查权限
    if not check_permission('CUSTOMER_LEAD_MANAGEMENT'):
        return jsonify({'success': False, 'message': '权限不足！'}), 403
    
    lead = db.session.get(CustomerLead, lead_id)
    if not lead:
        return jsonify({'success': False, 'message': '客资记录不存在！'}), 404
    
    try:
        db.session.delete(lead)
        db.session.commit()
        return jsonify({'success': True, 'message': '客资删除成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'}), 500
