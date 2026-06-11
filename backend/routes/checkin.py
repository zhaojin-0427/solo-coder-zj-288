from flask import Blueprint, request, jsonify
from models import Guest, CheckInRecord, db
from datetime import datetime

checkin_bp = Blueprint('checkin', __name__)

@checkin_bp.route('/<int:guest_id>', methods=['POST'])
def checkin_guest(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    data = request.get_json()

    previous_status = guest.checkin_status
    previous_count = guest.actual_arrival_count

    new_status = data.get('status', 'checked_in')
    actual_count = data.get('actual_count')
    operator_id = data.get('operator_id')
    remark = data.get('remark', '')

    guest.checkin_status = new_status
    guest.checkin_time = datetime.utcnow()
    guest.checkin_by = operator_id

    if actual_count is not None:
        guest.actual_arrival_count = actual_count
    elif new_status == 'checked_in' and previous_status == 'pending':
        guest.actual_arrival_count = guest.companion_count + 1

    count_change = guest.actual_arrival_count - previous_count

    record = CheckInRecord(
        wedding_id=guest.wedding_id,
        guest_id=guest.id,
        checkin_type='checkin',
        previous_status=previous_status,
        new_status=new_status,
        previous_count=previous_count,
        new_count=guest.actual_arrival_count,
        count_change=count_change,
        operator_id=operator_id,
        remark=remark
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({
        'guest': guest.to_dict(),
        'record': record.to_dict()
    })

@checkin_bp.route('/<int:guest_id>/status', methods=['PUT'])
def update_checkin_status(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    data = request.get_json()

    previous_status = guest.checkin_status
    previous_count = guest.actual_arrival_count

    new_status = data.get('status')
    actual_count = data.get('actual_count')
    operator_id = data.get('operator_id')
    remark = data.get('remark', '')

    if new_status:
        guest.checkin_status = new_status
        if new_status == 'checked_in' and not guest.checkin_time:
            guest.checkin_time = datetime.utcnow()
            guest.checkin_by = operator_id

    if actual_count is not None:
        guest.actual_arrival_count = actual_count

    count_change = guest.actual_arrival_count - previous_count

    if new_status != previous_status or count_change != 0:
        record = CheckInRecord(
            wedding_id=guest.wedding_id,
            guest_id=guest.id,
            checkin_type='update',
            previous_status=previous_status,
            new_status=new_status or previous_status,
            previous_count=previous_count,
            new_count=guest.actual_arrival_count,
            count_change=count_change,
            operator_id=operator_id,
            remark=remark
        )
        db.session.add(record)

    db.session.commit()

    return jsonify(guest.to_dict())

@checkin_bp.route('/records', methods=['GET'])
def get_checkin_records():
    wedding_id = request.args.get('wedding_id', type=int)
    guest_id = request.args.get('guest_id', type=int)
    limit = request.args.get('limit', type=int, default=50)

    query = CheckInRecord.query

    if wedding_id:
        query = query.filter_by(wedding_id=wedding_id)
    if guest_id:
        query = query.filter_by(guest_id=guest_id)

    records = query.order_by(CheckInRecord.created_at.desc()).limit(limit).all()
    return jsonify([r.to_dict() for r in records])

@checkin_bp.route('/stats', methods=['GET'])
def get_checkin_stats():
    wedding_id = request.args.get('wedding_id', type=int)
    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400

    guests = Guest.query.filter_by(wedding_id=wedding_id).all()

    total_guests = len(guests)
    total_expected = sum(g.companion_count + 1 for g in guests)

    checked_in_count = sum(1 for g in guests if g.checkin_status == 'checked_in')
    late_count = sum(1 for g in guests if g.checkin_status == 'late')
    absent_count = sum(1 for g in guests if g.checkin_status == 'absent')
    pending_count = sum(1 for g in guests if g.checkin_status == 'pending')
    temp_changed_count = sum(1 for g in guests if g.checkin_status == 'changed')

    total_arrived = sum(g.actual_arrival_count for g in guests if g.checkin_status in ['checked_in', 'late'])

    arrival_rate = round((total_arrived / total_expected * 100) if total_expected > 0 else 0, 1)
    checkin_rate = round(((checked_in_count + late_count) / total_guests * 100) if total_guests > 0 else 0, 1)

    temp_added = sum(
        max(0, g.actual_arrival_count - (g.companion_count + 1))
        for g in guests
        if g.checkin_status in ['checked_in', 'late'] and g.actual_arrival_count > g.companion_count + 1
    )
    temp_reduced = sum(
        max(0, (g.companion_count + 1) - g.actual_arrival_count)
        for g in guests
        if g.checkin_status in ['checked_in', 'late', 'absent'] and g.actual_arrival_count < g.companion_count + 1
    )

    high_priority_guests = [g.to_dict() for g in guests if g.is_high_priority]
    high_priority_arrived = sum(1 for g in high_priority_guests if g['checkin_status'] in ['checked_in', 'late'])
    high_priority_pending = sum(1 for g in high_priority_guests if g['checkin_status'] == 'pending')

    return jsonify({
        'total_guests': total_guests,
        'total_expected': total_expected,
        'total_arrived': total_arrived,
        'arrival_rate': arrival_rate,
        'checkin_rate': checkin_rate,
        'checked_in_count': checked_in_count,
        'late_count': late_count,
        'absent_count': absent_count,
        'pending_count': pending_count,
        'temp_changed_count': temp_changed_count,
        'temp_added': temp_added,
        'temp_reduced': temp_reduced,
        'high_priority_total': len(high_priority_guests),
        'high_priority_arrived': high_priority_arrived,
        'high_priority_pending': high_priority_pending,
        'high_priority_guests': high_priority_guests
    })

@checkin_bp.route('/search', methods=['GET'])
def search_guests_for_checkin():
    wedding_id = request.args.get('wedding_id', type=int)
    keyword = request.args.get('keyword', '')

    if not wedding_id:
        return jsonify({'error': '缺少 wedding_id 参数'}), 400

    query = Guest.query.filter_by(wedding_id=wedding_id)

    if keyword:
        query = query.filter(
            (Guest.name.contains(keyword)) |
            (Guest.phone.contains(keyword))
        )

    guests = query.order_by(Guest.name.asc()).all()
    return jsonify([g.to_dict() for g in guests])

@checkin_bp.route('/batch', methods=['POST'])
def batch_checkin():
    data = request.get_json()
    guest_ids = data.get('guest_ids', [])
    status = data.get('status', 'checked_in')
    operator_id = data.get('operator_id')
    remark = data.get('remark', '')

    updated_guests = []
    for guest_id in guest_ids:
        guest = Guest.query.get(guest_id)
        if guest:
            previous_status = guest.checkin_status
            previous_count = guest.actual_arrival_count

            guest.checkin_status = status
            if status == 'checked_in' and not guest.checkin_time:
                guest.checkin_time = datetime.utcnow()
                guest.checkin_by = operator_id
                guest.actual_arrival_count = guest.companion_count + 1

            count_change = guest.actual_arrival_count - previous_count

            record = CheckInRecord(
                wedding_id=guest.wedding_id,
                guest_id=guest.id,
                checkin_type='batch_checkin',
                previous_status=previous_status,
                new_status=status,
                previous_count=previous_count,
                new_count=guest.actual_arrival_count,
                count_change=count_change,
                operator_id=operator_id,
                remark=remark
            )
            db.session.add(record)
            updated_guests.append(guest)

    db.session.commit()
    return jsonify([g.to_dict() for g in updated_guests])
