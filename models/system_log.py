from models.db import db
from datetime import datetime

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    security_id = db.Column(db.String(20), db.ForeignKey('security_guards.security_id'))
    staff_id = db.Column(db.String(20), db.ForeignKey('department_staff.staff_id'))
    action = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45))
    related_department_id = db.Column(db.String(20), db.ForeignKey('departments.department_id'))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
