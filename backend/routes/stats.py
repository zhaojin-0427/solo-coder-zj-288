from flask import Blueprint, request, jsonify
from models import Wedding, Task, Bridesmaid, TimelineNode, TaskAdjustment, BudgetCategory, ExpenseReimbursement, db
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
