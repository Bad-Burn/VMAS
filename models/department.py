from models.db import db
from datetime import datetime

class Department(db.Model):
    __tablename__ = 'departments'
    
    department_id = db.Column(db.String(20), primary_key=True)
    department_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.Enum('active', 'inactive'), default='active')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    staff = db.relationship('DepartmentStaff', backref='department', lazy=True)
    registrations = db.relationship('VisitorRegistration', backref='department', lazy=True)
    system_logs = db.relationship('SystemLog', backref='department', lazy=True)
