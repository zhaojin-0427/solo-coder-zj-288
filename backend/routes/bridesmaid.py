from flask import Blueprint, request, jsonify
from models import Bridesmaid, db
from datetime import datetime

bridesmaid_bp = Blueprint('bridesmaid', __name__)

@bridesmaid_bp.route('/', methods=['GET'])
def get_bridesmaids():
    wedding_id = request.args.get('wedding_id', type=int)
    query = Bridesmaid.query
    if wedding_id:
        query = query.filter_by(wedding_id=wedding_id)
    bridesmaids = query.all()
    return jsonify([b.to_dict() for b in bridesmaids])

@bridesmaid_bp.route('/<int:bridesmaid_id>', methods=['GET'])
def get_bridesmaid(bridesmaid_id):
    bridesmaid = Bridesmaid.query.get_or_404(bridesmaid_id)
    result = bridesmaid.to_dict()
    result['tasks'] = [t.to_dict() for t in bridesmaid.tasks]
    return jsonify(result)

@bridesmaid_bp.route('/', methods=['POST'])
def create_bridesmaid():
    data = request.get_json()
    bridesmaid = Bridesmaid(
        wedding_id=data['wedding_id'],
        name=data['name'],
        phone=data.get('phone', ''),
        role=data.get('role', 'member'),
        avatar=data.get('avatar', '')
    )
    db.session.add(bridesmaid)
    db.session.commit()
    return jsonify(bridesmaid.to_dict()), 201

@bridesmaid_bp.route('/<int:bridesmaid_id>', methods=['PUT'])
def update_bridesmaid(bridesmaid_id):
    bridesmaid = Bridesmaid.query.get_or_404(bridesmaid_id)
    data = request.get_json()
    if 'name' in data:
        bridesmaid.name = data['name']
    if 'phone' in data:
        bridesmaid.phone = data['phone']
    if 'role' in data:
        bridesmaid.role = data['role']
    if 'avatar' in data:
        bridesmaid.avatar = data['avatar']
    db.session.commit()
    return jsonify(bridesmaid.to_dict())

@bridesmaid_bp.route('/<int:bridesmaid_id>', methods=['DELETE'])
def delete_bridesmaid(bridesmaid_id):
    bridesmaid = Bridesmaid.query.get_or_404(bridesmaid_id)
    db.session.delete(bridesmaid)
    db.session.commit()
    return jsonify({'message': '伴娘信息已删除'})

@bridesmaid_bp.route('/<int:bridesmaid_id>/tasks', methods=['GET'])
def get_bridesmaid_tasks(bridesmaid_id):
    bridesmaid = Bridesmaid.query.get_or_404(bridesmaid_id)
    tasks = [t.to_dict() for t in bridesmaid.tasks]
    return jsonify(tasks)
