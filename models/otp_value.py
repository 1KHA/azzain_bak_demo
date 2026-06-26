from datetime import datetime
from database import db

class OtpValue(db.Model):
    __tablename__ = 'otp_value'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.String, nullable=False)
    is_verified = db.Column(db.Boolean,default=False)
    expiry_at = db.Column(db.TIMESTAMP, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)