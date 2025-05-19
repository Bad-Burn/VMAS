from models.db import db
from datetime import datetime

class SecurityGuard(db.Model):
    __tablename__ = 'security_guards'
    
    security_id = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    approved_registrations = db.relationship('VisitorRegistration', backref='security_guard', lazy=True)
    system_logs = db.relationship('SystemLog', backref='security_guard', lazy=True)
