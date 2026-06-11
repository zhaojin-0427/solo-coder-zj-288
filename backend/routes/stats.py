from flask import Blueprint, request, jsonify
from models import Wedding, Task, Bridesmaid, TimelineNode, TaskAdjustment, BudgetCategory, ExpenseReimbursement, Material, MaterialBorrowing, Guest, Table, db
from datetime import date, datetime
from sqlalchemy import func
from routes.risk import calculate_wedding_risk

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/overview', methods=['GET'])
def get_overview_stats():
    wedding_id = request.args.get('wedding_id', type=int)
    
    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400
    
    total_tasks = Task.query.filter_by(wedding_id=wedding_id).count()
    completed_tasks = Task.query.filter_by(wedding_id=wedding_id, status='completed').count()
    in_progress_tasks = Task.query.filter_by(wedding_id=wedding_id, status='in_progress').count()
    pending_tasks = Task.query.filter_by(wedding_id=wedding_id, status='pending').count()
    
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    total_adjustments = db.session.query(TaskAdjustment).join(Task).filter(Task.wedding_id == wedding_id).count()
    
    overdue_tasks = Task.query.filter(
        Task.wedding_id == wedding_id,
        Task.due_date.isnot(None),
        Task.due_date < date.today(),
        Task.status != 'completed'
    ).count()
    
    timeline_nodes = TimelineNode.query.filter_by(wedding_id=wedding_id).count()
    bridesmaids_count = Bridesmaid.query.filter_by(wedding_id=wedding_id).count()
    
    return jsonify({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'pending_tasks': pending_tasks,
        'completion_rate': round(completion_rate, 1),
        'total_adjustments': total_adjustments,
        'overdue_tasks': overdue_tasks,
        'timeline_nodes': timeline_nodes,
        'bridesmaids_count': bridesmaids_count
    })

@stats_bp.route('/workload', methods=['GET'])
def get_workload_distribution():
    wedding_id = request.args.get('wedding_id', type=int)
    
    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400
    
    bridesmaids = Bridesmaid.query.filter_by(wedding_id=wedding_id).all()
    
    workload_data = []
    for bridesmaid in bridesmaids:
        tasks = Task.query.filter_by(wedding_id=wedding_id, assigned_to=bridesmaid.id).all()
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == 'completed')
        in_progress = sum(1 for t in tasks if t.status == 'in_progress')
        
        total_progress = sum(t.progress for t in tasks)
        avg_progress = (total_progress / total) if total > 0 else 0
        
        workload_data.append({
            'bridesmaid_id': bridesmaid.id,
            'name': bridesmaid.name,
            'role': bridesmaid.role,
            'total_tasks': total,
            'completed_tasks': completed,
            'in_progress_tasks': in_progress,
            'pending_tasks': total - completed - in_progress,
            'avg_progress': round(avg_progress, 1),
            'completion_rate': round((completed / total * 100) if total > 0 else 0, 1)
        })
    
    workload_data.sort(key=lambda x: x['total_tasks'], reverse=True)
    
    return jsonify(workload_data)

@stats_bp.route('/by-category', methods=['GET'])
def get_stats_by_category():
    wedding_id = request.args.get('wedding_id', type=int)
    
    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400
    
    tasks = Task.query.filter_by(wedding_id=wedding_id).all()
    
    category_stats = {}
    for task in tasks:
        cat = task.category
        if cat not in category_stats:
            category_stats[cat] = {
                'category': cat,
                'total': 0,
                'completed': 0,
                'in_progress': 0,
                'pending': 0
            }
        category_stats[cat]['total'] += 1
        if task.status == 'completed':
            category_stats[cat]['completed'] += 1
        elif task.status == 'in_progress':
            category_stats[cat]['in_progress'] += 1
        else:
            category_stats[cat]['pending'] += 1
    
    return jsonify(list(category_stats.values()))

@stats_bp.route('/overdue-tasks', methods=['GET'])
def get_overdue_tasks():
    wedding_id = request.args.get('wedding_id', type=int)
    
    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400
    
    today = date.today()
    overdue_tasks = Task.query.filter(
        Task.wedding_id == wedding_id,
        Task.due_date.isnot(None),
        Task.due_date < today,
        Task.status != 'completed'
    ).order_by(Task.due_date.asc()).all()
    
    return jsonify([t.to_dict() for t in overdue_tasks])

@stats_bp.route('/adjustments', methods=['GET'])
def get_adjustment_history():
    wedding_id = request.args.get('wedding_id', type=int)
    
    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400
    
    adjustments = db.session.query(TaskAdjustment).join(Task).filter(
        Task.wedding_id == wedding_id
    ).order_by(TaskAdjustment.adjusted_at.desc()).all()
    
    result = []
    for adj in adjustments:
        adj_dict = adj.to_dict()
        task = Task.query.get(adj.task_id)
        if task:
            adj_dict['task_title'] = task.title
        
        if adj.previous_assignee:
            prev = Bridesmaid.query.get(adj.previous_assignee)
            adj_dict['previous_assignee_name'] = prev.name if prev else None
        
        if adj.new_assignee:
            new = Bridesmaid.query.get(adj.new_assignee)
            adj_dict['new_assignee_name'] = new.name if new else None
        
        result.append(adj_dict)
    
    return jsonify(result)

@stats_bp.route('/risk-distribution', methods=['GET'])
def get_risk_distribution():
    wedding_id = request.args.get('wedding_id', type=int)

    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400

    today = date.today()
    wedding = Wedding.query.get_or_404(wedding_id)
    tasks = Task.query.filter_by(wedding_id=wedding_id).all()

    risk = calculate_wedding_risk(wedding_id)

    high_risk_tasks = []
    for task in tasks:
        risk_reason = None
        if task.priority == 'high' and task.status != 'completed' and task.due_date and task.due_date < today:
            risk_reason = '关键任务逾期'
        elif task.category == 'logistics' and task.due_date and task.due_date < today and task.status != 'completed':
            risk_reason = '材料不足'

        if risk_reason:
            assigned_name = None
            if task.assigned_bridesmaid:
                assigned_name = task.assigned_bridesmaid.name
            high_risk_tasks.append({
                'id': task.id,
                'title': task.title,
                'category': task.category,
                'priority': task.priority,
                'risk_reason': risk_reason,
                'assigned_name': assigned_name
            })

    risk_breakdown = {
        'delivery_date_risk': 0,
        'task_overdue_risk': 0,
        'progress_behind_risk': 0,
        'material_shortage_risk': 0
    }

    if '交付日期临近' in risk['risk_reasons']:
        risk_breakdown['delivery_date_risk'] = 1
    if '关键任务逾期' in risk['risk_reasons']:
        risk_breakdown['task_overdue_risk'] = risk['details']['overdue_critical_tasks']
    if '作品完成数量落后' in risk['risk_reasons']:
        risk_breakdown['progress_behind_risk'] = 1
    if '材料不足' in risk['risk_reasons']:
        risk_breakdown['material_shortage_risk'] = risk['details']['overdue_logistics_tasks']

    risk_distribution = {'low': 0, 'medium': 0, 'high': 0}
    risk_distribution[risk['risk_level']] = 1

    return jsonify({
        'risk_distribution': risk_distribution,
        'high_risk_count': risk_distribution['high'],
        'high_risk_tasks': high_risk_tasks,
        'risk_breakdown': risk_breakdown
    })

@stats_bp.route('/budget-stats', methods=['GET'])
def get_budget_stats():
    wedding_id = request.args.get('wedding_id', type=int)
    
    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400
    
    categories = BudgetCategory.query.filter_by(wedding_id=wedding_id).all()
    
    total_budget = sum(c.budget_limit for c in categories)
    total_approved = sum(sum(e.amount for e in c.expenses if e.status == 'approved') for c in categories)
    total_pending = sum(sum(e.amount for e in c.expenses if e.status == 'pending') for c in categories)
    total_rejected = sum(sum(e.amount for e in c.expenses if e.status == 'rejected') for c in categories)
    total_used = total_approved + total_pending
    
    over_budget_count = sum(1 for c in categories if (sum(e.amount for e in c.expenses if e.status == 'approved') + sum(e.amount for e in c.expenses if e.status == 'pending')) > c.budget_limit)
    
    pending_expenses = ExpenseReimbursement.query.filter_by(
        wedding_id=wedding_id,
        status='pending'
    ).count()
    
    expense_by_category = []
    for c in categories:
        approved = sum(e.amount for e in c.expenses if e.status == 'approved')
        pending = sum(e.amount for e in c.expenses if e.status == 'pending')
        used = approved + pending
        usage_rate = (used / c.budget_limit * 100) if c.budget_limit > 0 else 0
        expense_by_category.append({
            'category_id': c.id,
            'name': c.name,
            'color': c.color,
            'icon': c.icon,
            'budget_limit': c.budget_limit,
            'approved_amount': round(approved, 2),
            'pending_amount': round(pending, 2),
            'remaining': round(c.budget_limit - used, 2),
            'usage_rate': round(usage_rate, 1),
            'is_over_budget': used > c.budget_limit,
            'expense_count': len(c.expenses)
        })
    
    return jsonify({
        'total_budget': round(total_budget, 2),
        'total_approved': round(total_approved, 2),
        'total_pending': round(total_pending, 2),
        'total_rejected': round(total_rejected, 2),
        'total_remaining': round(total_budget - total_used, 2),
        'overall_usage_rate': round((total_used / total_budget * 100) if total_budget > 0 else 0, 1),
        'over_budget_count': over_budget_count,
        'pending_expense_count': pending_expenses,
        'category_count': len(categories),
        'expense_by_category': expense_by_category
    })

@stats_bp.route('/material-stats', methods=['GET'])
def get_material_stats():
    wedding_id = request.args.get('wedding_id', type=int)

    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400

    materials = Material.query.filter_by(wedding_id=wedding_id).all()
    borrowings = MaterialBorrowing.query.filter_by(wedding_id=wedding_id).all()

    total_items = len(materials)
    total_quantity = sum(m.total_quantity for m in materials)
    total_borrowed = sum(m.to_dict()['borrowed_quantity'] for m in materials)
    total_available = total_quantity - total_borrowed

    usage_rate = round((total_borrowed / total_quantity * 100) if total_quantity > 0 else 0, 1)

    overdue_count = sum(1 for b in borrowings if b.status == 'overdue')
    abnormal_count = sum(1 for b in borrowings if b.status == 'returned' and b.returned_quantity < b.borrowed_quantity)

    material_borrow_counts = {}
    for b in borrowings:
        name = b.material.name if b.material else '未知'
        material_borrow_counts[name] = material_borrow_counts.get(name, 0) + 1

    top_materials = sorted(material_borrow_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_borrowed = [{'name': name, 'count': count} for name, count in top_materials]

    return jsonify({
        'total_items': total_items,
        'total_quantity': total_quantity,
        'total_borrowed': total_borrowed,
        'total_available': total_available,
        'usage_rate': usage_rate,
        'overdue_count': overdue_count,
        'abnormal_count': abnormal_count,
        'top_borrowed': top_borrowed
    })

@stats_bp.route('/guest-stats', methods=['GET'])
def get_guest_stats():
    wedding_id = request.args.get('wedding_id', type=int)

    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400

    guests = Guest.query.filter_by(wedding_id=wedding_id).all()
    tables = Table.query.filter_by(wedding_id=wedding_id).all()

    total_guests = len(guests)
    total_expected = sum(g.companion_count + 1 for g in guests)

    checked_in_count = sum(1 for g in guests if g.checkin_status == 'checked_in')
    late_count = sum(1 for g in guests if g.checkin_status == 'late')
    absent_count = sum(1 for g in guests if g.checkin_status == 'absent')
    pending_count = sum(1 for g in guests if g.checkin_status == 'pending')
    changed_count = sum(1 for g in guests if g.checkin_status == 'changed')

    total_arrived = sum(
        g.actual_arrival_count for g in guests
        if g.checkin_status in ['checked_in', 'late']
    )

    arrival_rate = round((total_arrived / total_expected * 100) if total_expected > 0 else 0, 1)
    checkin_rate = round(
        ((checked_in_count + late_count) / total_guests * 100) if total_guests > 0 else 0,
        1
    )

    temp_added = sum(
        max(0, g.actual_arrival_count - (g.companion_count + 1))
        for g in guests
        if g.checkin_status in ['checked_in', 'late']
        and g.actual_arrival_count > g.companion_count + 1
    )
    temp_reduced = sum(
        max(0, (g.companion_count + 1) - g.actual_arrival_count)
        for g in guests
        if g.checkin_status in ['checked_in', 'late', 'absent']
        and g.actual_arrival_count < g.companion_count + 1
    )

    high_priority_total = sum(1 for g in guests if g.is_high_priority)
    high_priority_arrived = sum(
        1 for g in guests
        if g.is_high_priority and g.checkin_status in ['checked_in', 'late']
    )
    high_priority_pending = sum(
        1 for g in guests
        if g.is_high_priority and g.checkin_status == 'pending'
    )
    high_priority_guests = [
        g.to_dict() for g in guests if g.is_high_priority
    ]

    groups = {}
    for guest in guests:
        group = guest.group_name or '未分组'
        if group not in groups:
            groups[group] = {
                'group_name': group,
                'guest_count': 0,
                'total_people': 0,
                'checked_in': 0,
                'arrived_people': 0
            }
        groups[group]['guest_count'] += 1
        groups[group]['total_people'] += guest.companion_count + 1
        if guest.checkin_status in ['checked_in', 'late']:
            groups[group]['checked_in'] += 1
            groups[group]['arrived_people'] += guest.actual_arrival_count

    group_stats = list(groups.values())
    group_stats.sort(key=lambda x: x['total_people'], reverse=True)

    table_stats = []
    for table in tables:
        table_data = table.to_dict()
        table_stats.append({
            'table_id': table.id,
            'table_name': table.name,
            'capacity': table_data['capacity'],
            'assigned_count': table_data['assigned_count'],
            'checked_in_count': table_data['checked_in_count'],
            'available_seats': table_data['available_seats'],
            'is_over_capacity': table_data['is_over_capacity'],
            'seating_rate': table_data['seating_rate'],
            'guest_count': table_data['guest_count']
        })
    table_stats.sort(key=lambda x: x['table_name'])

    unassigned_guests = [
        g.to_dict() for g in guests if g.table_id is None
    ]

    total_tables = len(tables)
    total_capacity = sum(t.capacity for t in tables)
    total_assigned = sum(
        g.companion_count + 1 for g in guests if g.table_id is not None
    )
    over_capacity_count = sum(
        1 for t in table_stats if t['is_over_capacity']
    )
    overall_seating_rate = round(
        (total_assigned / total_capacity * 100) if total_capacity > 0 else 0,
        1
    )

    return jsonify({
        'total_guests': total_guests,
        'total_expected': total_expected,
        'total_arrived': total_arrived,
        'arrival_rate': arrival_rate,
        'checkin_rate': checkin_rate,
        'checked_in_count': checked_in_count,
        'late_count': late_count,
        'absent_count': absent_count,
        'pending_count': pending_count,
        'changed_count': changed_count,
        'temp_added': temp_added,
        'temp_reduced': temp_reduced,
        'high_priority_total': high_priority_total,
        'high_priority_arrived': high_priority_arrived,
        'high_priority_pending': high_priority_pending,
        'high_priority_guests': high_priority_guests,
        'group_stats': group_stats,
        'table_stats': table_stats,
        'total_tables': total_tables,
        'total_capacity': total_capacity,
        'total_assigned': total_assigned,
        'over_capacity_count': over_capacity_count,
        'overall_seating_rate': overall_seating_rate,
        'unassigned_guest_count': len(unassigned_guests),
        'unassigned_guests': unassigned_guests
    })
