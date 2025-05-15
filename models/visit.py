from datetime import datetime
from models.db import db

class Visit(db.Model):
    __tablename__ = 'visit'
    
    id = db.Column(db.String(50), primary_key=True)
    visitor_id = db.Column(db.String(7), db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    contact_no = db.Column(db.String(20), nullable=False)
    purpose = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_in = db.Column(db.DateTime, nullable=True)
    time_out = db.Column(db.DateTime, nullable=True)
