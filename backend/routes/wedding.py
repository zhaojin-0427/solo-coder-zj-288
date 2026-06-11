from flask import Blueprint, request, jsonify
from models import Wedding, db
from datetime import datetime
from routes.risk import calculate_wedding_risk

wedding_bp = Blueprint('wedding', __name__)

@wedding_bp.route('/', methods=['GET'])
def get_weddings():
    weddings = Wedding.query.all()
    result = []
    for w in weddings:
        w_dict = w.to_dict()
        risk = calculate_wedding_risk(w.id)
        w_dict['risk_level'] = risk['risk_level']
        w_dict['risk_reasons'] = risk['risk_reasons']
        result.append(w_dict)
    return jsonify(result)

@wedding_bp.route('/<int:wedding_id>', methods=['GET'])
def get_wedding(wedding_id):
    wedding = Wedding.query.get_or_404(wedding_id)
    w_dict = wedding.to_dict()
    risk = calculate_wedding_risk(wedding_id)
    w_dict['risk_level'] = risk['risk_level']
    w_dict['risk_reasons'] = risk['risk_reasons']
    return jsonify(w_dict)

@wedding_bp.route('/', methods=['POST'])
def create_wedding():
    data = request.get_json()
    wedding = Wedding(
        bride_name=data['bride_name'],
        groom_name=data['groom_name'],
        wedding_date=datetime.strptime(data['wedding_date'], '%Y-%m-%d').date(),
        venue=data.get('venue', ''),
        description=data.get('description', '')
    )
    db.session.add(wedding)
    db.session.commit()
    return jsonify(wedding.to_dict()), 201

@wedding_bp.route('/<int:wedding_id>', methods=['PUT'])
def update_wedding(wedding_id):
    wedding = Wedding.query.get_or_404(wedding_id)
    data = request.get_json()
    if 'bride_name' in data:
        wedding.bride_name = data['bride_name']
    if 'groom_name' in data:
        wedding.groom_name = data['groom_name']
    if 'wedding_date' in data:
        wedding.wedding_date = datetime.strptime(data['wedding_date'], '%Y-%m-%d').date()
    if 'venue' in data:
        wedding.venue = data['venue']
    if 'description' in data:
        wedding.description = data['description']
    db.session.commit()
    return jsonify(wedding.to_dict())

@wedding_bp.route('/<int:wedding_id>', methods=['DELETE'])
def delete_wedding(wedding_id):
    wedding = Wedding.query.get_or_404(wedding_id)
    db.session.delete(wedding)
    db.session.commit()
    return jsonify({'message': 'Wedding deleted successfully'})
