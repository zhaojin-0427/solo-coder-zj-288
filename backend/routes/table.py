from flask import Blueprint, request, jsonify
from models import Table, Guest, db

table_bp = Blueprint('table', __name__)

@table_bp.route('/', methods=['GET'])
def get_tables():
    wedding_id = request.args.get('wedding_id', type=int)
    table_type = request.args.get('table_type')

    query = Table.query
    if wedding_id:
        query = query.filter_by(wedding_id=wedding_id)
    if table_type:
        query = query.filter_by(table_type=table_type)

    tables = query.order_by(Table.name.asc()).all()
    return jsonify([t.to_dict() for t in tables])

@table_bp.route('/<int:table_id>', methods=['GET'])
def get_table(table_id):
    table = Table.query.get_or_404(table_id)
    result = table.to_dict()
    result['guests'] = [g.to_dict() for g in table.guests]
    return jsonify(result)

@table_bp.route('/', methods=['POST'])
def create_table():
    data = request.get_json()
    table = Table(
        wedding_id=data['wedding_id'],
        name=data['name'],
        capacity=data.get('capacity', 10),
        table_type=data.get('table_type', 'normal'),
        location=data.get('location', ''),
        notes=data.get('notes', '')
    )
    db.session.add(table)
    db.session.commit()
    return jsonify(table.to_dict()), 201

@table_bp.route('/<int:table_id>', methods=['PUT'])
def update_table(table_id):
    table = Table.query.get_or_404(table_id)
    data = request.get_json()
    if 'name' in data:
        table.name = data['name']
    if 'capacity' in data:
        table.capacity = data['capacity']
    if 'table_type' in data:
        table.table_type = data['table_type']
    if 'location' in data:
        table.location = data['location']
    if 'notes' in data:
        table.notes = data['notes']
    db.session.commit()
    return jsonify(table.to_dict())

@table_bp.route('/<int:table_id>', methods=['DELETE'])
def delete_table(table_id):
    table = Table.query.get_or_404(table_id)
    for guest in table.guests:
        guest.table_id = None
    db.session.delete(table)
    db.session.commit()
    return jsonify({'message': '桌位已删除'})

@table_bp.route('/batch', methods=['POST'])
def batch_create_tables():
    data = request.get_json()
    wedding_id = data.get('wedding_id')
    start_num = data.get('start_num', 1)
    count = data.get('count', 10)
    capacity = data.get('capacity', 10)
    prefix = data.get('prefix', '第')
    suffix = data.get('suffix', '桌')

    created_tables = []
    for i in range(count):
        table_num = start_num + i
        table = Table(
            wedding_id=wedding_id,
            name=f'{prefix}{table_num}{suffix}',
            capacity=capacity,
            table_type='normal'
        )
        db.session.add(table)
        created_tables.append(table)

    db.session.commit()
    return jsonify([t.to_dict() for t in created_tables]), 201

@table_bp.route('/overview', methods=['GET'])
def get_tables_overview():
    wedding_id = request.args.get('wedding_id', type=int)
    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400

    tables = Table.query.filter_by(wedding_id=wedding_id).all()
    total_tables = len(tables)
    total_capacity = sum(t.capacity for t in tables)
    total_assigned = sum(t.to_dict()['assigned_count'] for t in tables)
    total_checked_in = sum(t.to_dict()['checked_in_count'] for t in tables)
    over_capacity_count = sum(1 for t in tables if t.to_dict()['is_over_capacity'])

    unassigned_guests = Guest.query.filter(
        Guest.wedding_id == wedding_id,
        Guest.table_id.is_(None)
    ).count()

    return jsonify({
        'total_tables': total_tables,
        'total_capacity': total_capacity,
        'total_assigned': total_assigned,
        'total_checked_in': total_checked_in,
        'available_seats': total_capacity - total_assigned,
        'over_capacity_count': over_capacity_count,
        'unassigned_guests': unassigned_guests,
        'overall_seating_rate': round((total_assigned / total_capacity * 100) if total_capacity > 0 else 0, 1)
    })
