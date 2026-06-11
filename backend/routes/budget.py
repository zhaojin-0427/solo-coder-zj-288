from flask import Blueprint, request, jsonify, current_app
from models import BudgetCategory, ExpenseReimbursement, Bridesmaid, Task, db
from datetime import datetime
import os
from werkzeug.utils import secure_filename

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/categories', methods=['GET'])
def get_categories():
    wedding_id = request.args.get('wedding_id', type=int)
    
    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400
    
    categories = BudgetCategory.query.filter_by(wedding_id=wedding_id).order_by(BudgetCategory.created_at.asc()).all()
    return jsonify([c.to_dict() for c in categories])

@budget_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = BudgetCategory.query.get_or_404(category_id)
    return jsonify(category.to_dict())

@budget_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    
    if not data.get('wedding_id') or not data.get('name'):
        return jsonify({'error': '缺少必要参数'}), 400
    
    category = BudgetCategory(
        wedding_id=data['wedding_id'],
        name=data['name'],
        icon=data.get('icon', '💰'),
        color=data.get('color', '#409eff'),
        budget_limit=data.get('budget_limit', 0),
        description=data.get('description', ''),
        created_by=data.get('created_by')
    )
    
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201

@budget_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = BudgetCategory.query.get_or_404(category_id)
    data = request.get_json()
    
    if 'name' in data:
        category.name = data['name']
    if 'icon' in data:
        category.icon = data['icon']
    if 'color' in data:
        category.color = data['color']
    if 'budget_limit' in data:
        category.budget_limit = data['budget_limit']
    if 'description' in data:
        category.description = data['description']
    
    db.session.commit()
    return jsonify(category.to_dict())

@budget_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = BudgetCategory.query.get_or_404(category_id)
    
    if category.expenses:
        return jsonify({'error': '该分类下已有费用记录，无法删除'}), 400
    
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': '分类已删除'})

@budget_bp.route('/expenses', methods=['GET'])
def get_expenses():
    wedding_id = request.args.get('wedding_id', type=int)
    category_id = request.args.get('category_id', type=int)
    task_id = request.args.get('task_id', type=int)
    status = request.args.get('status')
    submitted_by = request.args.get('submitted_by', type=int)
    
    query = ExpenseReimbursement.query
    
    if wedding_id:
        query = query.filter_by(wedding_id=wedding_id)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if task_id:
        query = query.filter_by(task_id=task_id)
    if status:
        query = query.filter_by(status=status)
    if submitted_by:
        query = query.filter_by(submitted_by=submitted_by)
    
    expenses = query.order_by(ExpenseReimbursement.created_at.desc()).all()
    return jsonify([e.to_dict() for e in expenses])

@budget_bp.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    expense = ExpenseReimbursement.query.get_or_404(expense_id)
    return jsonify(expense.to_dict())

@budget_bp.route('/expenses', methods=['POST'])
def create_expense():
    data = request.get_json()
    
    if not data.get('wedding_id') or not data.get('category_id') or not data.get('amount') or not data.get('purpose') or not data.get('submitted_by'):
        return jsonify({'error': '缺少必要参数'}), 400
    
    expense = ExpenseReimbursement(
        wedding_id=data['wedding_id'],
        category_id=data['category_id'],
        task_id=data.get('task_id'),
        amount=float(data['amount']),
        purpose=data['purpose'],
        payment_method=data.get('payment_method', ''),
        receipt_url=data.get('receipt_url', ''),
        submitted_by=data['submitted_by'],
        status='pending'
    )
    
    db.session.add(expense)
    db.session.commit()
    return jsonify(expense.to_dict()), 201

@budget_bp.route('/expenses/<int:expense_id>/review', methods=['POST'])
def review_expense(expense_id):
    expense = ExpenseReimbursement.query.get_or_404(expense_id)
    data = request.get_json()
    
    if not data.get('status') or not data.get('reviewed_by'):
        return jsonify({'error': '缺少必要参数'}), 400
    
    if data['status'] not in ['approved', 'rejected']:
        return jsonify({'error': '无效的审核状态'}), 400
    
    expense.status = data['status']
    expense.reviewed_by = data['reviewed_by']
    expense.review_comment = data.get('review_comment', '')
    expense.reviewed_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(expense.to_dict())

@budget_bp.route('/expenses/<int:expense_id>/upload-receipt', methods=['POST'])
def upload_receipt(expense_id):
    expense = ExpenseReimbursement.query.get_or_404(expense_id)
    
    if 'receipt' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['receipt']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file:
        filename = secure_filename(f"receipt_{expense_id}_{int(datetime.now().timestamp())}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        receipt_url = f"/static/uploads/{filename}"
        expense.receipt_url = receipt_url
        db.session.commit()
        
        return jsonify({'receipt_url': receipt_url, 'expense': expense.to_dict()})
    
    return jsonify({'error': '上传失败'}), 500

@budget_bp.route('/summary', methods=['GET'])
def get_budget_summary():
    wedding_id = request.args.get('wedding_id', type=int)
    
    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400
    
    categories = BudgetCategory.query.filter_by(wedding_id=wedding_id).all()
    
    total_budget = sum(c.budget_limit for c in categories)
    total_approved = sum(c.to_dict()['approved_amount'] for c in categories)
    total_pending = sum(c.to_dict()['pending_amount'] for c in categories)
    total_remaining = total_budget - total_approved
    
    over_budget_count = sum(1 for c in categories if c.to_dict()['is_over_budget'])
    
    expense_distribution = []
    for c in categories:
        cd = c.to_dict()
        expense_distribution.append({
            'category_id': c.id,
            'name': c.name,
            'color': c.color,
            'approved_amount': cd['approved_amount'],
            'pending_amount': cd['pending_amount'],
            'budget_limit': cd['budget_limit'],
            'usage_rate': cd['usage_rate'],
            'is_over_budget': cd['is_over_budget']
        })
    
    pending_expenses = ExpenseReimbursement.query.filter_by(
        wedding_id=wedding_id,
        status='pending'
    ).count()
    
    return jsonify({
        'total_budget': round(total_budget, 2),
        'total_approved': round(total_approved, 2),
        'total_pending': round(total_pending, 2),
        'total_remaining': round(total_remaining, 2),
        'overall_usage_rate': round((total_approved / total_budget * 100) if total_budget > 0 else 0, 1),
        'over_budget_count': over_budget_count,
        'pending_expense_count': pending_expenses,
        'expense_distribution': expense_distribution,
        'category_count': len(categories)
    })
