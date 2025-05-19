from models.db import db
from datetime import datetime

class Visitor(db.Model):
    __tablename__ = 'visitors'
    
    visitor_id = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    visitor_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text)
    contact_no = db.Column(db.String(20))
    qr_code_path = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    registrations = db.relationship('VisitorRegistration', backref='visitor', lazy=True)
    qr_codes = db.relationship('VisitorQR', backref='visitor', lazy=True)
