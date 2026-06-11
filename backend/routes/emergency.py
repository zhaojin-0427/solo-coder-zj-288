from flask import Blueprint, request, jsonify
from models import EmergencyContact, db

emergency_bp = Blueprint('emergency', __name__)

@emergency_bp.route('/contacts', methods=['GET'])
def get_contacts():
    wedding_id = request.args.get('wedding_id', type=int)
    query = EmergencyContact.query
    if wedding_id:
        query = query.filter_by(wedding_id=wedding_id)
    contacts = query.order_by(EmergencyContact.is_primary.desc(), EmergencyContact.created_at.asc()).all()
    return jsonify([c.to_dict() for c in contacts])

@emergency_bp.route('/contacts', methods=['POST'])
def create_contact():
    data = request.get_json()
    contact = EmergencyContact(
        wedding_id=data['wedding_id'],
        name=data['name'],
        phone=data['phone'],
        role=data.get('role', ''),
        is_primary=data.get('is_primary', False)
    )
    db.session.add(contact)
    db.session.commit()
    return jsonify(contact.to_dict()), 201

@emergency_bp.route('/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    contact = EmergencyContact.query.get_or_404(contact_id)
    data = request.get_json()
    if 'name' in data:
        contact.name = data['name']
    if 'phone' in data:
        contact.phone = data['phone']
    if 'role' in data:
        contact.role = data['role']
    if 'is_primary' in data:
        if data['is_primary']:
            EmergencyContact.query.filter_by(wedding_id=contact.wedding_id).update({'is_primary': False})
        contact.is_primary = data['is_primary']
    db.session.commit()
    return jsonify(contact.to_dict())

@emergency_bp.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    contact = EmergencyContact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'message': '联系人已删除'})
