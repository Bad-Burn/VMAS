from models.db import db
from datetime import datetime

class Visitor(db.Model):
    __tablename__ = 'visitor'
    
    id = db.Column(db.String(50), primary_key=True)  # Format: V123456
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    contact_no = db.Column(db.String(20))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default='visitor')
    
    # Relationships
    visits = db.relationship('Visit', backref='visitor', lazy=True)
    qr_code = db.relationship('VisitorQR', backref='visitor', uselist=False)
