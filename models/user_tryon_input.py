from database import db, ma
from datetime import datetime
from marshmallow import fields

class UserTryonInput(db.Model):
    __tablename__ = 'user_tryon_input'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    image_url = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class UserTryonInputSchema(ma.Schema):
    class Meta:
        fields = ('id', 'user_id', 'image_url', 'created_at')
        model = UserTryonInput