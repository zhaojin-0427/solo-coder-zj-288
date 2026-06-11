from models import Wedding, Bridesmaid, Task, TimelineNode, TimelineAssignment, EmergencyContact, BudgetCategory, ExpenseReimbursement, Material, MaterialBorrowing, TaskMaterial, TimelineNodeMaterial, Guest, Table, CheckInRecord, db
from datetime import datetime, date, time

def seed_database():
    if Wedding.query.first():
        return
    
    wedding = Wedding(
        bride_name='张美丽',
        groom_name='李英俊',
        wedding_date=date(2025, 10, 1),
        venue='喜来登大酒店 · 宴会厅',
        description='一场浪漫温馨的婚礼，邀请伴娘团共同参与筹备'
    )
    db.session.add(wedding)
    db.session.flush()
    
    bridesmaids_data = [
        {'name': '王小雨', 'phone': '13800138001', 'role': 'leader', 'avatar': '👩‍🦰'},
        {'name': '刘思琪', 'phone': '13800138002', 'role': 'member', 'avatar': '👩‍🦱'},
        {'name': '陈梦瑶', 'phone': '13800138003', 'role': 'member', 'avatar': '👩'},
        {'name': '杨雪婷', 'phone': '13800138004', 'role': 'member', 'avatar': '👩‍🦳'},
        {'name': '赵嘉怡', 'phone': '13800138005', 'role': 'member', 'avatar': '👩‍🦲'},
    ]
    
    bridesmaids = []
    for bm_data in bridesmaids_data:
        bm = Bridesmaid(
            wedding_id=wedding.id,
            name=bm_data['name'],
            phone=bm_data['phone'],
            role=bm_data['role'],
            avatar=bm_data['avatar']
        )
        db.session.add(bm)
        bridesmaids.append(bm)
    db.session.flush()
    
    tasks_data = [
        {
            'title': '设计堵门游戏方案',
            'description': '准备3-5个有趣的堵门游戏，包括道具和游戏规则',
            'category': 'door_game',
            'priority': 'high',
            'due_date': date(2025, 9, 20),
            'status': 'in_progress',
            'progress': 60,
            'assigned_to': bridesmaids[0].id
        },
        {
            'title': '准备堵门红包',
            'description': '准备不同面额的堵门红包，预计50个左右',
            'category': 'door_game',
            'priority': 'medium',
            'due_date': date(2025, 9, 28),
            'status': 'pending',
            'progress': 0
        },
        {
            'title': '采购拍照道具',
            'description': '气球、手持拍照道具、花环、墨镜等创意拍照道具',
            'category': 'photo_props',
            'priority': 'medium',
            'due_date': date(2025, 9, 25),
            'status': 'completed',
            'progress': 100,
            'assigned_to': bridesmaids[1].id
        },
        {
            'title': '整理拍照pose清单',
            'description': '收集整理适合婚礼当天的拍照姿势和造型',
            'category': 'photo_props',
            'priority': 'low',
            'due_date': date(2025, 9, 28),
            'status': 'in_progress',
            'progress': 40,
            'assigned_to': bridesmaids[2].id
        },
        {
            'title': '准备应急医药包',
            'description': '创可贴、止痛药、肠胃药、晕车药、碘伏棉签等',
            'category': 'emergency_kit',
            'priority': 'high',
            'due_date': date(2025, 9, 26),
            'status': 'completed',
            'progress': 100,
            'assigned_to': bridesmaids[3].id
        },
        {
            'title': '准备补妆用品',
            'description': '口红、粉饼、吸油纸、发胶等补妆用品',
            'category': 'emergency_kit',
            'priority': 'medium',
            'due_date': date(2025, 9, 28),
            'status': 'in_progress',
            'progress': 70,
            'assigned_to': bridesmaids[4].id
        },
        {
            'title': '接亲路线踩点',
            'description': '提前走一遍接亲路线，计算时间，确认路况',
            'category': 'route_check',
            'priority': 'high',
            'due_date': date(2025, 9, 15),
            'status': 'completed',
            'progress': 100,
            'assigned_to': bridesmaids[0].id
        },
        {
            'title': '确认酒店停车位',
            'description': '确认酒店停车位数量和位置，制作停车指引',
            'category': 'route_check',
            'priority': 'medium',
            'due_date': date(2025, 9, 20),
            'status': 'pending',
            'progress': 0
        },
        {
            'title': '新房气球布置',
            'description': '用气球和鲜花装饰新房，营造浪漫氛围',
            'category': 'decoration',
            'priority': 'medium',
            'due_date': date(2025, 9, 30),
            'status': 'pending',
            'progress': 0
        },
        {
            'title': '婚房喜字贴放',
            'description': '确认喜字、拉花的位置和数量，提前贴好',
            'category': 'decoration',
            'priority': 'low',
            'due_date': date(2025, 9, 29),
            'status': 'pending',
            'progress': 0
        },
        {
            'title': '采购喜糖',
            'description': '根据宾客数量采购喜糖，准备包装盒',
            'category': 'logistics',
            'priority': 'high',
            'due_date': date(2025, 9, 10),
            'status': 'completed',
            'progress': 100,
            'assigned_to': bridesmaids[1].id
        },
        {
            'title': '整理伴手礼',
            'description': '将伴手礼装袋整理，按桌数分配',
            'category': 'logistics',
            'priority': 'medium',
            'due_date': date(2025, 9, 28),
            'status': 'in_progress',
            'progress': 50,
            'assigned_to': bridesmaids[2].id
        },
    ]
    
    for task_data in tasks_data:
        task = Task(wedding_id=wedding.id, **task_data)
        db.session.add(task)
    db.session.flush()
    
    timeline_data = [
        {
            'title': '新娘化妆',
            'description': '化妆师到达，开始新娘妆发造型',
            'start_time': time(5, 30),
            'end_time': time(7, 30),
            'location': '新娘家',
            'order_index': 0,
            'status': 'upcoming',
            'assignees': [bridesmaids[0].id]
        },
        {
            'title': '摄影师到达',
            'description': '摄影师到达新娘家，开始拍摄准备过程',
            'start_time': time(7, 0),
            'end_time': time(7, 30),
            'location': '新娘家',
            'order_index': 1,
            'status': 'upcoming',
            'assignees': []
        },
        {
            'title': '迎亲车队出发',
            'description': '新郎带领迎亲车队从新郎家出发',
            'start_time': time(7, 30),
            'end_time': time(8, 0),
            'location': '新郎家',
            'order_index': 2,
            'status': 'upcoming',
            'assignees': [bridesmaids[1].id]
        },
        {
            'title': '堵门游戏',
            'description': '伴娘团设置堵门关卡，新郎闯关接新娘',
            'start_time': time(8, 0),
            'end_time': time(9, 0),
            'location': '新娘家',
            'order_index': 3,
            'status': 'upcoming',
            'assignees': [bridesmaids[0].id, bridesmaids[2].id, bridesmaids[3].id, bridesmaids[4].id]
        },
        {
            'title': '敬茶改口',
            'description': '新人向双方父母敬茶，改口叫爸妈',
            'start_time': time(9, 0),
            'end_time': time(9, 30),
            'location': '新娘家',
            'order_index': 4,
            'status': 'upcoming',
            'assignees': [bridesmaids[0].id]
        },
        {
            'title': '出发去酒店',
            'description': '新人及亲友出发前往婚礼酒店',
            'start_time': time(9, 30),
            'end_time': time(10, 0),
            'location': '前往酒店途中',
            'order_index': 5,
            'status': 'upcoming',
            'assignees': [bridesmaids[1].id, bridesmaids[2].id]
        },
        {
            'title': '迎宾',
            'description': '新人在酒店门口迎接宾客',
            'start_time': time(10, 0),
            'end_time': time(11, 0),
            'location': '酒店大堂',
            'order_index': 6,
            'status': 'upcoming',
            'assignees': [bridesmaids[3].id, bridesmaids[4].id]
        },
        {
            'title': '婚礼仪式',
            'description': '正式婚礼仪式，包括入场、交换戒指、宣誓等',
            'start_time': time(11, 8),
            'end_time': time(12, 0),
            'location': '宴会厅',
            'order_index': 7,
            'status': 'upcoming',
            'assignees': [bridesmaids[0].id, bridesmaids[1].id, bridesmaids[2].id, bridesmaids[3].id, bridesmaids[4].id]
        },
        {
            'title': '婚宴开始',
            'description': '宾客用餐，新人逐桌敬酒',
            'start_time': time(12, 0),
            'end_time': time(14, 0),
            'location': '宴会厅',
            'order_index': 8,
            'status': 'upcoming',
            'assignees': [bridesmaids[0].id, bridesmaids[2].id]
        },
        {
            'title': '游戏互动',
            'description': '婚宴中的游戏互动环节',
            'start_time': time(13, 0),
            'end_time': time(13, 30),
            'location': '宴会厅',
            'order_index': 9,
            'status': 'upcoming',
            'assignees': [bridesmaids[1].id, bridesmaids[3].id]
        },
        {
            'title': '婚礼结束',
            'description': '欢送宾客，整理物品',
            'start_time': time(14, 0),
            'end_time': time(15, 0),
            'location': '酒店',
            'order_index': 10,
            'status': 'upcoming',
            'assignees': [bridesmaids[0].id, bridesmaids[4].id]
        },
    ]
    
    for node_data in timeline_data:
        assignees = node_data.pop('assignees', [])
        node = TimelineNode(wedding_id=wedding.id, **node_data)
        db.session.add(node)
        db.session.flush()
        
        for bid in assignees:
            from models import TimelineAssignment
            ta = TimelineAssignment(
                timeline_node_id=node.id,
                bridesmaid_id=bid,
                role='负责人'
            )
            db.session.add(ta)
    
    contacts_data = [
        {'name': '王小雨', 'phone': '13800138001', 'role': '伴娘团长', 'is_primary': True},
        {'name': '张妈妈', 'phone': '13900139001', 'role': '新娘母亲', 'is_primary': False},
        {'name': '李爸爸', 'phone': '13700137001', 'role': '新郎父亲', 'is_primary': False},
        {'name': '陈司仪', 'phone': '13600136001', 'role': '婚礼主持人', 'is_primary': False},
        {'name': '赵摄影', 'phone': '13500135001', 'role': '婚礼摄影师', 'is_primary': False},
        {'name': '酒店经理', 'phone': '13400134001', 'role': '酒店对接人', 'is_primary': False},
    ]
    
    for contact_data in contacts_data:
        contact = EmergencyContact(wedding_id=wedding.id, **contact_data)
        db.session.add(contact)
    
    db.session.flush()
    
    budget_categories_data = [
        {'name': '堵门红包', 'icon': '🧧', 'color': '#ff6b6b', 'budget_limit': 2000, 'description': '堵门游戏用的红包费用', 'created_by': bridesmaids[0].id},
        {'name': '拍照道具', 'icon': '📸', 'color': '#4ecdc4', 'budget_limit': 800, 'description': '气球、手持道具等拍照用品', 'created_by': bridesmaids[0].id},
        {'name': '应急物资', 'icon': '🩹', 'color': '#ffe66d', 'budget_limit': 500, 'description': '医药包、补妆用品等应急物品', 'created_by': bridesmaids[0].id},
        {'name': '交通餐饮', 'icon': '🚗', 'color': '#95e1d3', 'budget_limit': 3000, 'description': '交通费用、餐饮费用', 'created_by': bridesmaids[0].id},
        {'name': '场地布置', 'icon': '💐', 'color': '#f38181', 'budget_limit': 5000, 'description': '新房装饰、喜字拉花等', 'created_by': bridesmaids[0].id},
        {'name': '物资采购', 'icon': '🛍️', 'color': '#aa96da', 'budget_limit': 8000, 'description': '喜糖、伴手礼等物资采购', 'created_by': bridesmaids[0].id},
    ]
    
    budget_categories = []
    for bc_data in budget_categories_data:
        bc = BudgetCategory(wedding_id=wedding.id, **bc_data)
        db.session.add(bc)
        budget_categories.append(bc)
    db.session.flush()
    
    tasks_map = {t.title: t for t in Task.query.filter_by(wedding_id=wedding.id).all()}
    
    expenses_data = [
        {
            'category_id': budget_categories[5].id,
            'task_id': tasks_map.get('采购喜糖').id,
            'amount': 2500,
            'purpose': '采购喜糖500份，含包装盒',
            'payment_method': '微信支付',
            'submitted_by': bridesmaids[1].id,
            'status': 'approved',
            'reviewed_by': bridesmaids[0].id,
            'review_comment': '票据齐全，金额合理',
            'reviewed_at': datetime(2025, 9, 12, 10, 30)
        },
        {
            'category_id': budget_categories[1].id,
            'task_id': tasks_map.get('采购拍照道具').id,
            'amount': 680,
            'purpose': '气球100个、手持拍照道具20个、花环10个',
            'payment_method': '支付宝',
            'submitted_by': bridesmaids[1].id,
            'status': 'approved',
            'reviewed_by': bridesmaids[0].id,
            'review_comment': '道具质量很好，符合预期',
            'reviewed_at': datetime(2025, 9, 26, 14, 20)
        },
        {
            'category_id': budget_categories[2].id,
            'task_id': tasks_map.get('准备应急医药包').id,
            'amount': 320,
            'purpose': '创可贴、止痛药、肠胃药、晕车药、碘伏棉签等',
            'payment_method': '现金',
            'submitted_by': bridesmaids[3].id,
            'status': 'approved',
            'reviewed_by': bridesmaids[0].id,
            'review_comment': '药品齐全，考虑周到',
            'reviewed_at': datetime(2025, 9, 27, 9, 15)
        },
        {
            'category_id': budget_categories[3].id,
            'task_id': tasks_map.get('接亲路线踩点').id,
            'amount': 150,
            'purpose': '接亲路线踩点打车费用',
            'payment_method': '微信支付',
            'submitted_by': bridesmaids[0].id,
            'status': 'approved',
            'reviewed_by': bridesmaids[0].id,
            'review_comment': '路线确认无误',
            'reviewed_at': datetime(2025, 9, 16, 11, 0)
        },
        {
            'category_id': budget_categories[0].id,
            'task_id': tasks_map.get('准备堵门红包').id,
            'amount': 1200,
            'purpose': '准备50个堵门红包，面额10元、20元、50元',
            'payment_method': '现金',
            'submitted_by': bridesmaids[0].id,
            'status': 'pending',
            'reviewed_by': None,
            'review_comment': None,
            'reviewed_at': None
        },
        {
            'category_id': budget_categories[2].id,
            'task_id': tasks_map.get('准备补妆用品').id,
            'amount': 280,
            'purpose': '口红、粉饼、吸油纸、发胶等补妆用品',
            'payment_method': '微信支付',
            'submitted_by': bridesmaids[4].id,
            'status': 'pending',
            'reviewed_by': None,
            'review_comment': None,
            'reviewed_at': None
        },
        {
            'category_id': budget_categories[4].id,
            'task_id': None,
            'amount': 800,
            'purpose': '采购喜字20张、拉花10条、气球50个用于新房布置',
            'payment_method': '淘宝',
            'submitted_by': bridesmaids[2].id,
            'status': 'rejected',
            'reviewed_by': bridesmaids[0].id,
            'review_comment': '请提供具体的购物清单和票据照片',
            'reviewed_at': datetime(2025, 9, 28, 16, 45)
        },
    ]
    
    for exp_data in expenses_data:
        exp = ExpenseReimbursement(
            wedding_id=wedding.id,
            category_id=exp_data['category_id'],
            task_id=exp_data['task_id'],
            amount=exp_data['amount'],
            purpose=exp_data['purpose'],
            payment_method=exp_data['payment_method'],
            submitted_by=exp_data['submitted_by'],
            status=exp_data['status'],
            reviewed_by=exp_data['reviewed_by'],
            review_comment=exp_data['review_comment'],
            reviewed_at=exp_data['reviewed_at']
        )
        db.session.add(exp)

    db.session.flush()

    materials_data = [
        {'name': '对讲机', 'total_quantity': 6, 'storage_location': '新娘房·储物柜A', 'person_in_charge': bridesmaids[0].id, 'notes': '婚礼当天各组通讯使用'},
        {'name': '充电宝', 'total_quantity': 10, 'storage_location': '新娘房·储物柜B', 'person_in_charge': bridesmaids[1].id, 'notes': '满电状态备用'},
        {'name': '补光灯', 'total_quantity': 3, 'storage_location': '宴会厅·舞台侧', 'person_in_charge': bridesmaids[2].id, 'notes': '拍照补光使用'},
        {'name': '拍照道具套装', 'total_quantity': 5, 'storage_location': '新娘房·道具箱', 'person_in_charge': bridesmaids[1].id, 'notes': '含手持牌、气球、花环等'},
        {'name': '应急药箱', 'total_quantity': 2, 'storage_location': '新娘房·随身包', 'person_in_charge': bridesmaids[3].id, 'notes': '创可贴、止痛药、肠胃药等'},
        {'name': '备用高跟鞋', 'total_quantity': 3, 'storage_location': '新娘房·鞋柜', 'person_in_charge': bridesmaids[4].id, 'notes': '37码1双、38码2双'},
    ]

    materials = []
    for mat_data in materials_data:
        mat = Material(wedding_id=wedding.id, **mat_data)
        db.session.add(mat)
        materials.append(mat)
    db.session.flush()

    borrowings_data = [
        {
            'material_id': materials[0].id,
            'borrower_name': '刘思琪',
            'borrowed_quantity': 2,
            'purpose': '接亲车队协调通讯',
            'expected_return_time': datetime(2025, 10, 1, 14, 0),
            'status': 'returned',
            'returned_quantity': 2,
            'returned_at': datetime(2025, 10, 1, 13, 30)
        },
        {
            'material_id': materials[0].id,
            'borrower_name': '杨雪婷',
            'borrowed_quantity': 1,
            'purpose': '宴会厅现场协调',
            'expected_return_time': datetime(2025, 10, 1, 15, 0),
            'status': 'borrowed',
            'returned_quantity': 0
        },
        {
            'material_id': materials[1].id,
            'borrower_name': '陈梦瑶',
            'borrowed_quantity': 3,
            'purpose': '拍照手机充电',
            'expected_return_time': datetime(2025, 10, 1, 13, 0),
            'status': 'returned',
            'returned_quantity': 2,
            'abnormal_note': '1个充电宝丢失，已赔偿',
            'returned_at': datetime(2025, 10, 1, 14, 0)
        },
        {
            'material_id': materials[2].id,
            'borrower_name': '赵摄影',
            'borrowed_quantity': 2,
            'purpose': '宴会厅拍照补光',
            'expected_return_time': datetime(2025, 10, 1, 12, 0),
            'status': 'overdue',
            'returned_quantity': 0
        },
        {
            'material_id': materials[3].id,
            'borrower_name': '陈梦瑶',
            'borrowed_quantity': 3,
            'purpose': '伴娘团合影拍摄',
            'expected_return_time': datetime(2025, 10, 1, 14, 0),
            'status': 'borrowed',
            'returned_quantity': 0
        },
    ]

    for bor_data in borrowings_data:
        bor = MaterialBorrowing(
            wedding_id=wedding.id,
            material_id=bor_data['material_id'],
            borrower_name=bor_data['borrower_name'],
            borrowed_quantity=bor_data['borrowed_quantity'],
            purpose=bor_data['purpose'],
            expected_return_time=bor_data['expected_return_time'],
            status=bor_data['status'],
            returned_quantity=bor_data['returned_quantity'],
            abnormal_note=bor_data.get('abnormal_note', ''),
            returned_at=bor_data.get('returned_at')
        )
        db.session.add(bor)

    db.session.flush()

    tasks_map = {t.title: t for t in Task.query.filter_by(wedding_id=wedding.id).all()}
    timeline_map = {t.title: t for t in TimelineNode.query.filter_by(wedding_id=wedding.id).all()}
    materials_map = {m.name: m for m in Material.query.filter_by(wedding_id=wedding.id).all()}

    task_materials_data = [
        {'task_title': '采购拍照道具', 'material_name': '拍照道具套装', 'quantity_needed': 5, 'notes': '全部拍照道具'},
        {'task_title': '准备应急医药包', 'material_name': '应急药箱', 'quantity_needed': 2, 'notes': '应急使用'},
        {'task_title': '准备补妆用品', 'material_name': '补光灯', 'quantity_needed': 1, 'notes': '补光补妆'},
    ]

    for tm_data in task_materials_data:
        task = tasks_map.get(tm_data['task_title'])
        mat = materials_map.get(tm_data['material_name'])
        if task and mat:
            tm = TaskMaterial(
                task_id=task.id,
                material_id=mat.id,
                quantity_needed=tm_data['quantity_needed'],
                notes=tm_data.get('notes', '')
            )
            db.session.add(tm)

    timeline_materials_data = [
        {'timeline_title': '堵门游戏', 'material_name': '对讲机', 'quantity_needed': 3, 'notes': '堵门协调通讯'},
        {'timeline_title': '婚礼仪式', 'material_name': '对讲机', 'quantity_needed': 4, 'notes': '仪式现场协调'},
        {'timeline_title': '婚礼仪式', 'material_name': '补光灯', 'quantity_needed': 2, 'notes': '仪式现场补光'},
        {'timeline_title': '迎宾', 'material_name': '充电宝', 'quantity_needed': 3, 'notes': '迎宾签到充电'},
        {'timeline_title': '婚宴开始', 'material_name': '备用高跟鞋', 'quantity_needed': 1, 'notes': '敬酒备用'},
    ]

    for tnm_data in timeline_materials_data:
        node = timeline_map.get(tnm_data['timeline_title'])
        mat = materials_map.get(tnm_data['material_name'])
        if node and mat:
            tnm = TimelineNodeMaterial(
                timeline_node_id=node.id,
                material_id=mat.id,
                quantity_needed=tnm_data['quantity_needed'],
                notes=tnm_data.get('notes', '')
            )
            db.session.add(tnm)

    tables_data = [
        {'name': '主桌', 'capacity': 12, 'table_type': 'vip', 'location': '宴会厅中央', 'notes': '新人及双方父母'},
        {'name': '第1桌', 'capacity': 10, 'table_type': 'normal', 'location': '宴会厅左侧前排', 'notes': ''},
        {'name': '第2桌', 'capacity': 10, 'table_type': 'normal', 'location': '宴会厅左侧前排', 'notes': ''},
        {'name': '第3桌', 'capacity': 10, 'table_type': 'normal', 'location': '宴会厅左侧中排', 'notes': ''},
        {'name': '第4桌', 'capacity': 10, 'table_type': 'normal', 'location': '宴会厅左侧中排', 'notes': ''},
        {'name': '第5桌', 'capacity': 10, 'table_type': 'normal', 'location': '宴会厅右侧前排', 'notes': ''},
        {'name': '第6桌', 'capacity': 10, 'table_type': 'normal', 'location': '宴会厅右侧前排', 'notes': ''},
        {'name': '第7桌', 'capacity': 10, 'table_type': 'normal', 'location': '宴会厅右侧中排', 'notes': ''},
        {'name': '第8桌', 'capacity': 10, 'table_type': 'normal', 'location': '宴会厅右侧中排', 'notes': ''},
        {'name': '第9桌', 'capacity': 10, 'table_type': 'normal', 'location': '宴会厅后排', 'notes': ''},
        {'name': '第10桌', 'capacity': 10, 'table_type': 'normal', 'location': '宴会厅后排', 'notes': ''},
    ]

    tables = []
    for t_data in tables_data:
        t = Table(wedding_id=wedding.id, **t_data)
        db.session.add(t)
        tables.append(t)
    db.session.flush()

    table_map = {t.name: t for t in tables}

    guests_data = [
        {'name': '张建国', 'phone': '13900000001', 'group_name': '新娘家人', 'relation_tag': '父亲', 'companion_count': 1, 'table_name': '主桌', 'special_notes': '对海鲜过敏', 'is_high_priority': True},
        {'name': '李美丽', 'phone': '13900000002', 'group_name': '新娘家人', 'relation_tag': '母亲', 'companion_count': 0, 'table_name': '主桌', 'special_notes': '高血压，需清淡饮食', 'is_high_priority': True},
        {'name': '张卫国', 'phone': '13900000003', 'group_name': '新娘家人', 'relation_tag': '叔叔', 'companion_count': 2, 'table_name': '第1桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '张秀英', 'phone': '13900000004', 'group_name': '新娘家人', 'relation_tag': '姑姑', 'companion_count': 1, 'table_name': '第1桌', 'special_notes': '腿脚不便，需靠近通道', 'is_high_priority': True},
        {'name': '张伟', 'phone': '13900000005', 'group_name': '新娘家人', 'relation_tag': '堂弟', 'companion_count': 1, 'table_name': '第1桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '张娜', 'phone': '13900000006', 'group_name': '新娘家人', 'relation_tag': '堂妹', 'companion_count': 0, 'table_name': '第1桌', 'special_notes': '素食主义者', 'is_high_priority': False},
        {'name': '李国强', 'phone': '13800000001', 'group_name': '新郎家人', 'relation_tag': '父亲', 'companion_count': 1, 'table_name': '主桌', 'special_notes': '糖尿病，注意饮食', 'is_high_priority': True},
        {'name': '王秀兰', 'phone': '13800000002', 'group_name': '新郎家人', 'relation_tag': '母亲', 'companion_count': 0, 'table_name': '主桌', 'special_notes': '心脏不好，避免嘈杂', 'is_high_priority': True},
        {'name': '李明', 'phone': '13800000003', 'group_name': '新郎家人', 'relation_tag': '哥哥', 'companion_count': 2, 'table_name': '第5桌', 'special_notes': '带小孩，需要儿童座椅', 'is_high_priority': False},
        {'name': '李丽', 'phone': '13800000004', 'group_name': '新郎家人', 'relation_tag': '姐姐', 'companion_count': 1, 'table_name': '第5桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '李刚', 'phone': '13800000005', 'group_name': '新郎家人', 'relation_tag': '叔叔', 'companion_count': 2, 'table_name': '第5桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '王小雨', 'phone': '13800138001', 'group_name': '伴娘团', 'relation_tag': '伴娘团长', 'companion_count': 0, 'table_name': '第2桌', 'special_notes': '当天负责签到', 'is_high_priority': True},
        {'name': '刘思琪', 'phone': '13800138002', 'group_name': '伴娘团', 'relation_tag': '伴娘', 'companion_count': 0, 'table_name': '第2桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '陈梦瑶', 'phone': '13800138003', 'group_name': '伴娘团', 'relation_tag': '伴娘', 'companion_count': 0, 'table_name': '第2桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '杨雪婷', 'phone': '13800138004', 'group_name': '伴娘团', 'relation_tag': '伴娘', 'companion_count': 0, 'table_name': '第2桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '赵嘉怡', 'phone': '13800138005', 'group_name': '伴娘团', 'relation_tag': '伴娘', 'companion_count': 0, 'table_name': '第2桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '陈司仪', 'phone': '13600136001', 'group_name': '工作人员', 'relation_tag': '主持人', 'companion_count': 1, 'table_name': '第6桌', 'special_notes': '预留席位', 'is_high_priority': True},
        {'name': '赵摄影', 'phone': '13500135001', 'group_name': '工作人员', 'relation_tag': '摄影师', 'companion_count': 2, 'table_name': '第6桌', 'special_notes': '预留席位', 'is_high_priority': False},
        {'name': '王小军', 'phone': '13700001001', 'group_name': '新娘同事', 'relation_tag': '同事', 'companion_count': 1, 'table_name': '第3桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '李美玲', 'phone': '13700001002', 'group_name': '新娘同事', 'relation_tag': '同事', 'companion_count': 0, 'table_name': '第3桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '张大伟', 'phone': '13700001003', 'group_name': '新娘同事', 'relation_tag': '领导', 'companion_count': 1, 'table_name': '第3桌', 'special_notes': '公司总经理', 'is_high_priority': True},
        {'name': '刘小芳', 'phone': '13700001004', 'group_name': '新娘同事', 'relation_tag': '同事', 'companion_count': 2, 'table_name': '第3桌', 'special_notes': '带小孩，需要儿童座椅', 'is_high_priority': False},
        {'name': '陈志远', 'phone': '13700002001', 'group_name': '新郎同事', 'relation_tag': '同事', 'companion_count': 1, 'table_name': '第7桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '周婷婷', 'phone': '13700002002', 'group_name': '新郎同事', 'relation_tag': '同事', 'companion_count': 0, 'table_name': '第7桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '吴明辉', 'phone': '13700002003', 'group_name': '新郎同事', 'relation_tag': '领导', 'companion_count': 1, 'table_name': '第7桌', 'special_notes': '部门经理', 'is_high_priority': True},
        {'name': '郑浩', 'phone': '13700002004', 'group_name': '新郎同事', 'relation_tag': '同事', 'companion_count': 1, 'table_name': '第7桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '孙悦', 'phone': '13700003001', 'group_name': '新娘朋友', 'relation_tag': '闺蜜', 'companion_count': 1, 'table_name': '第4桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '马晓东', 'phone': '13700003002', 'group_name': '新娘朋友', 'relation_tag': '朋友', 'companion_count': 1, 'table_name': '第4桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '朱子轩', 'phone': '13700004001', 'group_name': '新郎朋友', 'relation_tag': '兄弟', 'companion_count': 1, 'table_name': '第8桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '林浩然', 'phone': '13700004002', 'group_name': '新郎朋友', 'relation_tag': '朋友', 'companion_count': 2, 'table_name': '第8桌', 'special_notes': '', 'is_high_priority': False},
        {'name': '黄晓雯', 'phone': '13700005001', 'group_name': '其他', 'relation_tag': '邻居', 'companion_count': 2, 'table_name': None, 'special_notes': '待确认是否出席', 'is_high_priority': False},
        {'name': '徐大伟', 'phone': '13700005002', 'group_name': '其他', 'relation_tag': '远房亲戚', 'companion_count': 3, 'table_name': None, 'special_notes': '待确认桌位', 'is_high_priority': False},
    ]

    for g_data in guests_data:
        table_name = g_data.pop('table_name', None)
        table_id = table_map[table_name].id if table_name and table_name in table_map else None
        guest = Guest(
            wedding_id=wedding.id,
            name=g_data['name'],
            phone=g_data.get('phone', ''),
            group_name=g_data.get('group_name', ''),
            relation_tag=g_data.get('relation_tag', ''),
            companion_count=g_data.get('companion_count', 0),
            table_id=table_id,
            special_notes=g_data.get('special_notes', ''),
            is_high_priority=g_data.get('is_high_priority', False)
        )
        db.session.add(guest)

    db.session.flush()

    db.session.commit()
    print('数据库初始化完成，已添加示例数据')
