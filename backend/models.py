from extensions import db
from datetime import datetime
import json

class Wedding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bride_name = db.Column(db.String(100), nullable=False)
    groom_name = db.Column(db.String(100), nullable=False)
    wedding_date = db.Column(db.Date, nullable=False)
    venue = db.Column(db.String(200))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    tasks = db.relationship('Task', backref='wedding', lazy=True, cascade='all, delete-orphan')
    timeline_nodes = db.relationship('TimelineNode', backref='wedding', lazy=True, cascade='all, delete-orphan')
    bridesmaids = db.relationship('Bridesmaid', backref='wedding', lazy=True, cascade='all, delete-orphan')
    emergency_contacts = db.relationship('EmergencyContact', backref='wedding', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'bride_name': self.bride_name,
            'groom_name': self.groom_name,
            'wedding_date': self.wedding_date.isoformat() if self.wedding_date else None,
            'venue': self.venue,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Bridesmaid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey('wedding.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(50), default='member')
    avatar = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    tasks = db.relationship('Task', backref='assigned_bridesmaid', lazy=True)
    timeline_assignments = db.relationship('TimelineAssignment', backref='bridesmaid', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'wedding_id': self.wedding_id,
            'name': self.name,
            'phone': self.phone,
            'role': self.role,
            'avatar': self.avatar,
            'task_count': len(self.tasks),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey('wedding.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')
    priority = db.Column(db.String(20), default='medium')
    progress = db.Column(db.Integer, default=0)
    due_date = db.Column(db.Date)
    assigned_to = db.Column(db.Integer, db.ForeignKey('bridesmaid.id'))
    photo_proof = db.Column(db.String(500))
    notes = db.Column(db.Text)
    is_overdue = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    adjustments = db.relationship('TaskAdjustment', backref='task', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        assigned_name = None
        if self.assigned_bridesmaid:
            assigned_name = self.assigned_bridesmaid.name
        return {
            'id': self.id,
            'wedding_id': self.wedding_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'status': self.status,
            'priority': self.priority,
            'progress': self.progress,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'assigned_to': self.assigned_to,
            'assigned_name': assigned_name,
            'photo_proof': self.photo_proof,
            'notes': self.notes,
            'is_overdue': self.is_overdue,
            'adjustment_count': len(self.adjustments),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class TaskAdjustment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    previous_assignee = db.Column(db.Integer)
    new_assignee = db.Column(db.Integer)
    reason = db.Column(db.String(500))
    adjusted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'previous_assignee': self.previous_assignee,
            'new_assignee': self.new_assignee,
            'reason': self.reason,
            'adjusted_at': self.adjusted_at.isoformat() if self.adjusted_at else None
        }

class TimelineNode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey('wedding.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time)
    location = db.Column(db.String(200))
    status = db.Column(db.String(20), default='upcoming')
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    assignments = db.relationship('TimelineAssignment', backref='timeline_node', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        assigned_bridesmaids = [a.bridesmaid.to_dict() for a in self.assignments]
        return {
            'id': self.id,
            'wedding_id': self.wedding_id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'location': self.location,
            'status': self.status,
            'order_index': self.order_index,
            'assigned_bridesmaids': assigned_bridesmaids,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class TimelineAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timeline_node_id = db.Column(db.Integer, db.ForeignKey('timeline_node.id'), nullable=False)
    bridesmaid_id = db.Column(db.Integer, db.ForeignKey('bridesmaid.id'), nullable=False)
    role = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'timeline_node_id': self.timeline_node_id,
            'bridesmaid_id': self.bridesmaid_id,
            'role': self.role,
            'bridesmaid': self.bridesmaid.to_dict() if self.bridesmaid else None
        }

class EmergencyContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wedding_id = db.Column(db.Integer, db.ForeignKey('wedding.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(100))
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'wedding_id': self.wedding_id,
            'name': self.name,
            'phone': self.phone,
            'role': self.role,
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
