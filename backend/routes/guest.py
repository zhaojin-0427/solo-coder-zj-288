from flask import Blueprint, request, jsonify
from models import Guest, Table, db
from datetime import datetime

guest_bp = Blueprint('guest', __name__)

@guest_bp.route('/', methods=['GET'])
def get_guests():
    wedding_id = request.args.get('wedding_id', type=int)
    group_name = request.args.get('group_name')
    table_id = request.args.get('table_id', type=int)
    relation_tag = request.args.get('relation_tag')
    keyword = request.args.get('keyword')
    checkin_status = request.args.get('checkin_status')
    is_high_priority = request.args.get('is_high_priority', type=bool)

    query = Guest.query

    if wedding_id:
        query = query.filter_by(wedding_id=wedding_id)
    if group_name:
        query = query.filter_by(group_name=group_name)
    if table_id is not None:
        if table_id == 0:
            query = query.filter(Guest.table_id.is_(None))
        else:
            query = query.filter_by(table_id=table_id)
    if relation_tag:
        query = query.filter_by(relation_tag=relation_tag)
    if keyword:
        query = query.filter(
            (Guest.name.contains(keyword)) |
            (Guest.phone.contains(keyword))
        )
    if checkin_status:
        query = query.filter_by(checkin_status=checkin_status)
    if is_high_priority is not None:
        query = query.filter_by(is_high_priority=is_high_priority)

    guests = query.order_by(Guest.created_at.desc()).all()
    return jsonify([g.to_dict() for g in guests])

@guest_bp.route('/<int:guest_id>', methods=['GET'])
def get_guest(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    result = guest.to_dict()
    result['checkin_records'] = [r.to_dict() for r in guest.checkin_records]
    return jsonify(result)

@guest_bp.route('/', methods=['POST'])
def create_guest():
    data = request.get_json()
    guest = Guest(
        wedding_id=data['wedding_id'],
        name=data['name'],
        phone=data.get('phone', ''),
        group_name=data.get('group_name', ''),
        relation_tag=data.get('relation_tag', ''),
        companion_count=data.get('companion_count', 0),
        table_id=data.get('table_id'),
        special_notes=data.get('special_notes', ''),
        is_high_priority=data.get('is_high_priority', False)
    )
    db.session.add(guest)
    db.session.commit()
    return jsonify(guest.to_dict()), 201

@guest_bp.route('/<int:guest_id>', methods=['PUT'])
def update_guest(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    data = request.get_json()
    if 'name' in data:
        guest.name = data['name']
    if 'phone' in data:
        guest.phone = data['phone']
    if 'group_name' in data:
        guest.group_name = data['group_name']
    if 'relation_tag' in data:
        guest.relation_tag = data['relation_tag']
    if 'companion_count' in data:
        guest.companion_count = data['companion_count']
    if 'table_id' in data:
        guest.table_id = data['table_id']
    if 'special_notes' in data:
        guest.special_notes = data['special_notes']
    if 'is_high_priority' in data:
        guest.is_high_priority = data['is_high_priority']
    db.session.commit()
    return jsonify(guest.to_dict())

@guest_bp.route('/<int:guest_id>', methods=['DELETE'])
def delete_guest(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    db.session.delete(guest)
    db.session.commit()
    return jsonify({'message': '宾客信息已删除'})

@guest_bp.route('/batch', methods=['POST'])
def batch_create_guests():
    data = request.get_json()
    guests_data = data.get('guests', [])
    wedding_id = data.get('wedding_id')

    created_guests = []
    for guest_data in guests_data:
        guest = Guest(
            wedding_id=wedding_id,
            name=guest_data['name'],
            phone=guest_data.get('phone', ''),
            group_name=guest_data.get('group_name', ''),
            relation_tag=guest_data.get('relation_tag', ''),
            companion_count=guest_data.get('companion_count', 0),
            table_id=guest_data.get('table_id'),
            special_notes=guest_data.get('special_notes', ''),
            is_high_priority=guest_data.get('is_high_priority', False)
        )
        db.session.add(guest)
        created_guests.append(guest)

    db.session.commit()
    return jsonify([g.to_dict() for g in created_guests]), 201

@guest_bp.route('/groups', methods=['GET'])
def get_guest_groups():
    wedding_id = request.args.get('wedding_id', type=int)
    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400

    guests = Guest.query.filter_by(wedding_id=wedding_id).all()
    groups = {}
    for guest in guests:
        group = guest.group_name or '未分组'
        if group not in groups:
            groups[group] = {
                'group_name': group,
                'guest_count': 0,
                'total_people': 0
            }
        groups[group]['guest_count'] += 1
        groups[group]['total_people'] += guest.companion_count + 1

    return jsonify(list(groups.values()))

@guest_bp.route('/unassigned-table', methods=['GET'])
def get_unassigned_table_guests():
    wedding_id = request.args.get('wedding_id', type=int)
    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400

    guests = Guest.query.filter(
        Guest.wedding_id == wedding_id,
        Guest.table_id.is_(None)
    ).all()
    return jsonify([g.to_dict() for g in guests])

@guest_bp.route('/assign-table', methods=['POST'])
def assign_table():
    data = request.get_json()
    guest_ids = data.get('guest_ids', [])
    table_id = data.get('table_id')

    for guest_id in guest_ids:
        guest = Guest.query.get(guest_id)
        if guest:
            guest.table_id = table_id

    db.session.commit()
    return jsonify({'message': '已分配桌位', 'assigned_count': len(guest_ids)})
