from flask import Blueprint, request, jsonify, current_app
from models import Task, TaskAdjustment, db
from datetime import datetime
import os
from werkzeug.utils import secure_filename

task_bp = Blueprint('task', __name__)

@task_bp.route('/', methods=['GET'])
def get_tasks():
    wedding_id = request.args.get('wedding_id', type=int)
    category = request.args.get('category')
    status = request.args.get('status')
    
    query = Task.query
    if wedding_id:
        query = query.filter_by(wedding_id=wedding_id)
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tasks])

@task_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@task_bp.route('/', methods=['POST'])
def create_task():
    data = request.get_json()
    due_date = None
    if data.get('due_date'):
        due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    
    task = Task(
        wedding_id=data['wedding_id'],
        title=data['title'],
        description=data.get('description', ''),
        category=data['category'],
        priority=data.get('priority', 'medium'),
        due_date=due_date
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201

@task_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'category' in data:
        task.category = data['category']
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    if 'progress' in data:
        task.progress = data['progress']
        if task.progress >= 100:
            task.status = 'completed'
        elif task.progress > 0:
            task.status = 'in_progress'
    if 'due_date' in data:
        if data['due_date']:
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        else:
            task.due_date = None
    if 'notes' in data:
        task.notes = data['notes']
    
    db.session.commit()
    return jsonify(task.to_dict())

@task_bp.route('/<int:task_id>/assign', methods=['POST'])
def assign_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    bridesmaid_id = data.get('bridesmaid_id')
    
    previous_assignee = task.assigned_to
    task.assigned_to = bridesmaid_id
    task.status = 'in_progress' if bridesmaid_id else 'pending'
    
    if bridesmaid_id and previous_assignee != bridesmaid_id:
        adjustment = TaskAdjustment(
            task_id=task_id,
            previous_assignee=previous_assignee,
            new_assignee=bridesmaid_id,
            reason=data.get('reason', '任务分配调整')
        )
        db.session.add(adjustment)
    
    db.session.commit()
    return jsonify(task.to_dict())

@task_bp.route('/<int:task_id>/claim', methods=['POST'])
def claim_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    bridesmaid_id = data.get('bridesmaid_id')
    
    if task.assigned_to:
        return jsonify({'error': '该任务已被认领'}), 400
    
    previous_assignee = task.assigned_to
    task.assigned_to = bridesmaid_id
    task.status = 'in_progress'
    task.progress = 10
    
    adjustment = TaskAdjustment(
        task_id=task_id,
        previous_assignee=previous_assignee,
        new_assignee=bridesmaid_id,
        reason='伴娘主动认领'
    )
    db.session.add(adjustment)
    db.session.commit()
    return jsonify(task.to_dict())

@task_bp.route('/<int:task_id>/progress', methods=['POST'])
def update_progress(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    progress = data.get('progress', 0)
    
    task.progress = progress
    if progress >= 100:
        task.status = 'completed'
    elif progress > 0:
        task.status = 'in_progress'
    
    db.session.commit()
    return jsonify(task.to_dict())

@task_bp.route('/<int:task_id>/upload-photo', methods=['POST'])
def upload_photo(task_id):
    task = Task.query.get_or_404(task_id)
    
    if 'photo' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file:
        filename = secure_filename(f"task_{task_id}_{int(datetime.now().timestamp())}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        photo_url = f"/static/uploads/{filename}"
        task.photo_proof = photo_url
        db.session.commit()
        
        return jsonify({'photo_url': photo_url, 'task': task.to_dict()})
    
    return jsonify({'error': '上传失败'}), 500

@task_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': '任务已删除'})

@task_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = [
        {'id': 'door_game', 'name': '堵门游戏', 'icon': '🎮', 'color': '#ff6b6b'},
        {'id': 'photo_props', 'name': '拍照道具', 'icon': '📸', 'color': '#4ecdc4'},
        {'id': 'emergency_kit', 'name': '应急包', 'icon': '🩹', 'color': '#ffe66d'},
        {'id': 'route_check', 'name': '接亲路线踩点', 'icon': '🗺️', 'color': '#95e1d3'},
        {'id': 'decoration', 'name': '场地布置', 'icon': '💐', 'color': '#f38181'},
        {'id': 'logistics', 'name': '物资采购', 'icon': '🛍️', 'color': '#aa96da'},
        {'id': 'reception', 'name': '接待宾客', 'icon': '👥', 'color': '#fcbad3'},
        {'id': 'other', 'name': '其他任务', 'icon': '📋', 'color': '#a8d8ea'}
    ]
    return jsonify(categories)
