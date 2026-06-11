from flask import Blueprint, request, jsonify
from models import TimelineNode, TimelineAssignment, Bridesmaid, db
from datetime import datetime

timeline_bp = Blueprint('timeline', __name__)

@timeline_bp.route('/', methods=['GET'])
def get_timeline():
    wedding_id = request.args.get('wedding_id', type=int)
    query = TimelineNode.query
    if wedding_id:
        query = query.filter_by(wedding_id=wedding_id)
    
    nodes = query.order_by(TimelineNode.order_index.asc(), TimelineNode.start_time.asc()).all()
    return jsonify([n.to_dict() for n in nodes])

@timeline_bp.route('/<int:node_id>', methods=['GET'])
def get_timeline_node(node_id):
    node = TimelineNode.query.get_or_404(node_id)
    return jsonify(node.to_dict())

@timeline_bp.route('/', methods=['POST'])
def create_timeline_node():
    data = request.get_json()
    
    start_time = datetime.strptime(data['start_time'], '%H:%M:%S').time()
    end_time = None
    if data.get('end_time'):
        end_time = datetime.strptime(data['end_time'], '%H:%M:%S').time()
    
    node = TimelineNode(
        wedding_id=data['wedding_id'],
        title=data['title'],
        description=data.get('description', ''),
        start_time=start_time,
        end_time=end_time,
        location=data.get('location', ''),
        order_index=data.get('order_index', 0)
    )
    db.session.add(node)
    db.session.commit()
    return jsonify(node.to_dict()), 201

@timeline_bp.route('/<int:node_id>', methods=['PUT'])
def update_timeline_node(node_id):
    node = TimelineNode.query.get_or_404(node_id)
    data = request.get_json()
    
    if 'title' in data:
        node.title = data['title']
    if 'description' in data:
        node.description = data['description']
    if 'start_time' in data:
        node.start_time = datetime.strptime(data['start_time'], '%H:%M:%S').time()
    if 'end_time' in data:
        if data['end_time']:
            node.end_time = datetime.strptime(data['end_time'], '%H:%M:%S').time()
        else:
            node.end_time = None
    if 'location' in data:
        node.location = data['location']
    if 'status' in data:
        node.status = data['status']
    if 'order_index' in data:
        node.order_index = data['order_index']
    
    db.session.commit()
    return jsonify(node.to_dict())

@timeline_bp.route('/<int:node_id>', methods=['DELETE'])
def delete_timeline_node(node_id):
    node = TimelineNode.query.get_or_404(node_id)
    db.session.delete(node)
    db.session.commit()
    return jsonify({'message': '流程节点已删除'})

@timeline_bp.route('/<int:node_id>/assign', methods=['POST'])
def assign_bridesmaid_to_node(node_id):
    node = TimelineNode.query.get_or_404(node_id)
    data = request.get_json()
    bridesmaid_ids = data.get('bridesmaid_ids', [])
    
    TimelineAssignment.query.filter_by(timeline_node_id=node_id).delete()
    
    for bid in bridesmaid_ids:
        assignment = TimelineAssignment(
            timeline_node_id=node_id,
            bridesmaid_id=bid,
            role=data.get('role', '负责人')
        )
        db.session.add(assignment)
    
    db.session.commit()
    return jsonify(node.to_dict())

@timeline_bp.route('/<int:node_id>/status', methods=['POST'])
def update_node_status(node_id):
    node = TimelineNode.query.get_or_404(node_id)
    data = request.get_json()
    node.status = data.get('status', node.status)
    db.session.commit()
    return jsonify(node.to_dict())

@timeline_bp.route('/reorder', methods=['POST'])
def reorder_timeline():
    data = request.get_json()
    node_order = data.get('node_order', [])
    
    for idx, node_id in enumerate(node_order):
        node = TimelineNode.query.get(node_id)
        if node:
            node.order_index = idx
    
    db.session.commit()
    return jsonify({'message': '排序已更新'})
