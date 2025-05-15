from datetime import datetime
from models.db import db

class VisitorQR(db.Model):
    __tablename__ = 'visitor_qr'
    
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.String(7), db.ForeignKey('user.id'), unique=True, nullable=False)
    qr_code = db.Column(db.Text, nullable=False)  # Base64 encoded QR code image
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime, nullable=True)
