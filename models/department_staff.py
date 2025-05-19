from models.db import db
from datetime import datetime

class DepartmentStaff(db.Model):
    __tablename__ = 'department_staff'
    
    staff_id = db.Column(db.String(20), primary_key=True)
    department_id = db.Column(db.String(20), db.ForeignKey('departments.department_id'), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    staff_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    system_logs = db.relationship('SystemLog', backref='staff', lazy=True)
