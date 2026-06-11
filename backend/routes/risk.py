from flask import Blueprint, request, jsonify
from models import Wedding, Task, Bridesmaid, db
from datetime import date, datetime, timedelta

risk_bp = Blueprint('risk', __name__)


def calculate_task_risk(task, wedding_date=None):
    today = date.today()
    
    risk_score = 0
    risk_reasons = []
    
    if task.due_date and task.due_date < today and task.status != 'completed':
        risk_score += 40
        if task.priority == 'high':
            risk_reasons.append('关键任务逾期')
        else:
            risk_reasons.append('任务逾期')
    
    if task.priority == 'high' and task.status != 'completed':
        risk_score += 20
    
    if task.due_date and task.status != 'completed':
        days_until_due = (task.due_date - today).days
        if days_until_due <= 3:
            risk_score += 30
            risk_reasons.append('交付日期临近')
        elif days_until_due <= 7:
            risk_score += 15
    
    if task.category == 'logistics' and task.status != 'completed':
        if task.due_date and task.due_date < today:
            risk_score += 20
            risk_reasons.append('材料不足')
        elif task.status == 'pending':
            risk_score += 10
    
    if task.progress < 30 and task.status == 'in_progress':
        risk_score += 15
        risk_reasons.append('作品完成数量落后')
    
    risk_score = min(risk_score, 100)
    
    if risk_score >= 60:
        risk_level = 'high'
    elif risk_score >= 30:
        risk_level = 'medium'
    else:
        risk_level = 'low'
    
    return {
        'risk_level': risk_level,
        'risk_score': risk_score,
        'risk_reasons': risk_reasons
    }


def calculate_wedding_risk(wedding_id):
    wedding = Wedding.query.get(wedding_id)
    if not wedding:
        return None

    today = date.today()
    tasks = Task.query.filter_by(wedding_id=wedding_id).all()
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == 'completed')
    overdue_tasks = sum(1 for t in tasks if t.due_date and t.due_date < today and t.status != 'completed')
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    days_until_wedding = (wedding.wedding_date - today).days

    risk_reasons = []
    risk_score = 0

    if days_until_wedding <= 7:
        risk_reasons.append('交付日期临近')
        risk_score += 40
    elif days_until_wedding <= 14:
        risk_reasons.append('交付日期临近')
        risk_score += 25
    elif days_until_wedding <= 30:
        risk_reasons.append('交付日期临近')
        risk_score += 10

    overdue_critical_tasks = [
        t for t in tasks
        if t.priority == 'high' and t.status != 'completed' and t.due_date and t.due_date < today
    ]
    if overdue_critical_tasks:
        risk_reasons.append('关键任务逾期')
        risk_score += min(len(overdue_critical_tasks) * 15, 35)

    if days_until_wedding <= 14 and completion_rate < 50:
        risk_reasons.append('作品完成数量落后')
        risk_score += 30
    elif days_until_wedding <= 30 and completion_rate < 30:
        risk_reasons.append('作品完成数量落后')
        risk_score += 20

    logistics_tasks = [t for t in tasks if t.category == 'logistics']
    overdue_logistics = [
        t for t in logistics_tasks
        if t.due_date and t.due_date < today and t.status != 'completed'
    ]
    pending_logistics = [t for t in logistics_tasks if t.status == 'pending']

    if overdue_logistics:
        risk_reasons.append('材料不足')
        risk_score += 20
    elif pending_logistics:
        risk_reasons.append('材料不足')
        risk_score += 10

    risk_score = min(risk_score, 100)

    if risk_score >= 60:
        risk_level = 'high'
    elif risk_score >= 30:
        risk_level = 'medium'
    else:
        risk_level = 'low'

    if not risk_reasons:
        risk_level = 'low'

    return {
        'wedding_id': wedding_id,
        'risk_level': risk_level,
        'risk_score': risk_score,
        'risk_reasons': risk_reasons,
        'details': {
            'days_until_wedding': days_until_wedding,
            'completion_rate': round(completion_rate, 1),
            'overdue_critical_tasks': len(overdue_critical_tasks),
            'pending_logistics_tasks': len(pending_logistics),
            'overdue_logistics_tasks': len(overdue_logistics),
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks
        }
    }


@risk_bp.route('/assessment', methods=['GET'])
def get_risk_assessment():
    wedding_id = request.args.get('wedding_id', type=int)
    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400

    result = calculate_wedding_risk(wedding_id)
    if not result:
        return jsonify({'error': '婚礼不存在'}), 404

    return jsonify(result)


@risk_bp.route('/overview', methods=['GET'])
def get_risk_overview():
    weddings = Wedding.query.all()
    risk_distribution = {'low': 0, 'medium': 0, 'high': 0}
    wedding_risks = []

    for wedding in weddings:
        risk = calculate_wedding_risk(wedding.id)
        risk_distribution[risk['risk_level']] += 1
        wedding_risks.append({
            'wedding_id': wedding.id,
            'bride_name': wedding.bride_name,
            'groom_name': wedding.groom_name,
            'wedding_date': wedding.wedding_date.isoformat() if wedding.wedding_date else None,
            'risk_level': risk['risk_level'],
            'risk_score': risk['risk_score'],
            'risk_reasons': risk['risk_reasons']
        })

    return jsonify({
        'risk_distribution': risk_distribution,
        'high_risk_count': risk_distribution['high'],
        'total_weddings': len(weddings),
        'weddings': wedding_risks
    })


@risk_bp.route('/high-risk-tasks', methods=['GET'])
def get_high_risk_tasks():
    wedding_id = request.args.get('wedding_id', type=int)
    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400

    today = date.today()
    tasks = Task.query.filter_by(wedding_id=wedding_id).all()
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
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'progress': task.progress,
                'risk_reason': risk_reason,
                'assigned_name': assigned_name
            })

    return jsonify({
        'wedding_id': wedding_id,
        'high_risk_tasks': high_risk_tasks
    })
