from flask import Blueprint, request, jsonify
from models import Material, MaterialBorrowing, TaskMaterial, TimelineNodeMaterial, db
from datetime import datetime

material_bp = Blueprint('material', __name__)

@material_bp.route('/items', methods=['GET'])
def get_materials():
    wedding_id = request.args.get('wedding_id', type=int)

    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400

    materials = Material.query.filter_by(wedding_id=wedding_id).order_by(Material.created_at.asc()).all()
    return jsonify([m.to_dict() for m in materials])

@material_bp.route('/items/<int:material_id>', methods=['GET'])
def get_material(material_id):
    material = Material.query.get_or_404(material_id)
    return jsonify(material.to_dict())

@material_bp.route('/items', methods=['POST'])
def create_material():
    data = request.get_json()

    if not data.get('wedding_id') or not data.get('name') or not data.get('total_quantity'):
        return jsonify({'error': '缺少必要参数'}), 400

    material = Material(
        wedding_id=data['wedding_id'],
        name=data['name'],
        total_quantity=data['total_quantity'],
        storage_location=data.get('storage_location', ''),
        person_in_charge=data.get('person_in_charge'),
        notes=data.get('notes', '')
    )

    db.session.add(material)
    db.session.commit()
    return jsonify(material.to_dict()), 201

@material_bp.route('/items/<int:material_id>', methods=['PUT'])
def update_material(material_id):
    material = Material.query.get_or_404(material_id)
    data = request.get_json()

    if 'name' in data:
        material.name = data['name']
    if 'total_quantity' in data:
        material.total_quantity = data['total_quantity']
    if 'storage_location' in data:
        material.storage_location = data['storage_location']
    if 'person_in_charge' in data:
        material.person_in_charge = data['person_in_charge']
    if 'notes' in data:
        material.notes = data['notes']

    db.session.commit()
    return jsonify(material.to_dict())

@material_bp.route('/items/<int:material_id>', methods=['DELETE'])
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)

    if material.borrowings:
        active = [b for b in material.borrowings if b.status != 'returned']
        if active:
            return jsonify({'error': '该物资有未归还的借用记录，无法删除'}), 400

    db.session.delete(material)
    db.session.commit()
    return jsonify({'message': '物资已删除'})

@material_bp.route('/borrowings', methods=['GET'])
def get_borrowings():
    wedding_id = request.args.get('wedding_id', type=int)
    material_id = request.args.get('material_id', type=int)
    status = request.args.get('status')

    query = MaterialBorrowing.query

    if wedding_id:
        query = query.filter_by(wedding_id=wedding_id)
    if material_id:
        query = query.filter_by(material_id=material_id)
    if status:
        query = query.filter_by(status=status)

    borrowings = query.order_by(MaterialBorrowing.created_at.desc()).all()

    now = datetime.utcnow()
    for b in borrowings:
        if b.status == 'borrowed' and b.expected_return_time and b.expected_return_time < now:
            b.status = 'overdue'
    db.session.commit()

    return jsonify([b.to_dict() for b in borrowings])

@material_bp.route('/borrowings', methods=['POST'])
def create_borrowing():
    data = request.get_json()

    if not data.get('material_id') or not data.get('borrower_name') or not data.get('borrowed_quantity'):
        return jsonify({'error': '缺少必要参数'}), 400

    material = Material.query.get_or_404(data['material_id'])

    if data['borrowed_quantity'] > material.to_dict()['available_quantity']:
        return jsonify({'error': '借用数量超过可用数量'}), 400

    expected_return_time = None
    if data.get('expected_return_time'):
        expected_return_time = datetime.strptime(data['expected_return_time'], '%Y-%m-%d %H:%M')

    borrowing = MaterialBorrowing(
        material_id=data['material_id'],
        wedding_id=material.wedding_id,
        borrower_name=data['borrower_name'],
        borrowed_quantity=data['borrowed_quantity'],
        purpose=data.get('purpose', ''),
        expected_return_time=expected_return_time,
        status='borrowed'
    )

    db.session.add(borrowing)
    db.session.commit()
    return jsonify(borrowing.to_dict()), 201

@material_bp.route('/borrowings/<int:borrowing_id>/return', methods=['POST'])
def return_borrowing(borrowing_id):
    borrowing = MaterialBorrowing.query.get_or_404(borrowing_id)
    data = request.get_json()

    if borrowing.status == 'returned':
        return jsonify({'error': '该记录已归还'}), 400

    returned_quantity = data.get('returned_quantity', borrowing.borrowed_quantity)
    if returned_quantity > borrowing.borrowed_quantity:
        return jsonify({'error': '归还数量不能超过借用数量'}), 400

    borrowing.returned_quantity = returned_quantity
    borrowing.abnormal_note = data.get('abnormal_note', '')
    borrowing.returned_at = datetime.utcnow()
    borrowing.status = 'returned'

    db.session.commit()
    return jsonify(borrowing.to_dict())

@material_bp.route('/summary', methods=['GET'])
def get_material_summary():
    wedding_id = request.args.get('wedding_id', type=int)

    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400

    materials = Material.query.filter_by(wedding_id=wedding_id).all()

    total_items = len(materials)
    total_quantity = sum(m.total_quantity for m in materials)
    total_borrowed = sum(m.to_dict()['borrowed_quantity'] for m in materials)
    total_available = total_quantity - total_borrowed

    overdue_borrowings = MaterialBorrowing.query.filter_by(wedding_id=wedding_id, status='overdue').count()
    abnormal_returns = MaterialBorrowing.query.filter_by(wedding_id=wedding_id, status='returned').filter(
        MaterialBorrowing.returned_quantity < MaterialBorrowing.borrowed_quantity
    ).count()

    return jsonify({
        'total_items': total_items,
        'total_quantity': total_quantity,
        'total_borrowed': total_borrowed,
        'total_available': total_available,
        'overdue_count': overdue_borrowings,
        'abnormal_count': abnormal_returns
    })

@material_bp.route('/overdue-alerts', methods=['GET'])
def get_overdue_alerts():
    wedding_id = request.args.get('wedding_id', type=int)

    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400

    now = datetime.utcnow()
    borrowings = MaterialBorrowing.query.filter_by(wedding_id=wedding_id).filter(
        MaterialBorrowing.status.in_(['borrowed', 'overdue'])
    ).all()

    alerts = []
    for b in borrowings:
        if b.expected_return_time and b.expected_return_time < now:
            if b.status != 'overdue':
                b.status = 'overdue'
            overdue_minutes = int((now - b.expected_return_time).total_seconds() / 60)
            alerts.append({
                'borrowing_id': b.id,
                'material_id': b.material_id,
                'material_name': b.material.name if b.material else None,
                'borrower_name': b.borrower_name,
                'borrowed_quantity': b.borrowed_quantity,
                'expected_return_time': b.expected_return_time.isoformat() if b.expected_return_time else None,
                'overdue_minutes': overdue_minutes,
                'status': b.status
            })

    db.session.commit()
    alerts.sort(key=lambda x: x['overdue_minutes'], reverse=True)
    return jsonify(alerts)

@material_bp.route('/abnormal-returns', methods=['GET'])
def get_abnormal_returns():
    wedding_id = request.args.get('wedding_id', type=int)

    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400

    abnormal = MaterialBorrowing.query.filter_by(wedding_id=wedding_id, status='returned').filter(
        MaterialBorrowing.returned_quantity < MaterialBorrowing.borrowed_quantity
    ).order_by(MaterialBorrowing.returned_at.desc()).all()

    result = []
    for b in abnormal:
        b_dict = b.to_dict()
        b_dict['loss_quantity'] = b.borrowed_quantity - b.returned_quantity
        result.append(b_dict)

    return jsonify(result)

@material_bp.route('/task-materials', methods=['GET'])
def get_task_materials():
    task_id = request.args.get('task_id', type=int)
    material_id = request.args.get('material_id', type=int)

    query = TaskMaterial.query
    if task_id:
        query = query.filter_by(task_id=task_id)
    if material_id:
        query = query.filter_by(material_id=material_id)

    links = query.all()
    return jsonify([l.to_dict() for l in links])

@material_bp.route('/task-materials', methods=['POST'])
def link_task_material():
    data = request.get_json()

    if not data.get('task_id') or not data.get('material_id'):
        return jsonify({'error': '缺少必要参数'}), 400

    existing = TaskMaterial.query.filter_by(
        task_id=data['task_id'],
        material_id=data['material_id']
    ).first()
    if existing:
        return jsonify({'error': '该物资已关联此任务'}), 400

    link = TaskMaterial(
        task_id=data['task_id'],
        material_id=data['material_id'],
        quantity_needed=data.get('quantity_needed', 1),
        notes=data.get('notes', '')
    )

    db.session.add(link)
    db.session.commit()
    return jsonify(link.to_dict()), 201

@material_bp.route('/task-materials/<int:link_id>', methods=['DELETE'])
def unlink_task_material(link_id):
    link = TaskMaterial.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    return jsonify({'message': '关联已解除'})

@material_bp.route('/timeline-materials', methods=['GET'])
def get_timeline_materials():
    timeline_node_id = request.args.get('timeline_node_id', type=int)
    material_id = request.args.get('material_id', type=int)

    query = TimelineNodeMaterial.query
    if timeline_node_id:
        query = query.filter_by(timeline_node_id=timeline_node_id)
    if material_id:
        query = query.filter_by(material_id=material_id)

    links = query.all()
    return jsonify([l.to_dict() for l in links])

@material_bp.route('/timeline-materials', methods=['POST'])
def link_timeline_material():
    data = request.get_json()

    if not data.get('timeline_node_id') or not data.get('material_id'):
        return jsonify({'error': '缺少必要参数'}), 400

    existing = TimelineNodeMaterial.query.filter_by(
        timeline_node_id=data['timeline_node_id'],
        material_id=data['material_id']
    ).first()
    if existing:
        return jsonify({'error': '该物资已关联此流程节点'}), 400

    link = TimelineNodeMaterial(
        timeline_node_id=data['timeline_node_id'],
        material_id=data['material_id'],
        quantity_needed=data.get('quantity_needed', 1),
        notes=data.get('notes', '')
    )

    db.session.add(link)
    db.session.commit()
    return jsonify(link.to_dict()), 201

@material_bp.route('/timeline-materials/<int:link_id>', methods=['DELETE'])
def unlink_timeline_material(link_id):
    link = TimelineNodeMaterial.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    return jsonify({'message': '关联已解除'})
