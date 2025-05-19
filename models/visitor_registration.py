from models.db import db
from datetime import datetime

class VisitorRegistration(db.Model):
    __tablename__ = 'visitor_registrations'
    
    registration_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_id = db.Column(db.String(20), db.ForeignKey('departments.department_id'), nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    time_in = db.Column(db.DateTime)
    time_out = db.Column(db.DateTime)
    status = db.Column(db.Enum('pending', 'approved', 'rejected', 'completed', 'active', 'verified'), default='pending')
    qr_code_path = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    approved_by_security_id = db.Column(db.String(20), db.ForeignKey('security_guards.security_id'))
    visitor_id = db.Column(db.String(20), db.ForeignKey('visitors.visitor_id'), nullable=False)
