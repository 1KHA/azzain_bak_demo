from database import db, ma
from datetime import datetime
from marshmallow import fields

class TryonOutput(db.Model):
    __tablename__ = 'tryon_output'
    id = db.Column(db.Integer, primary_key=True)
    user_tryon_input_id = db.Column(db.Integer, db.ForeignKey('user_tryon_input.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    image_url = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class TryonOutputSchema(ma.Schema):
    class Meta:
        fields = ( 'user_tryon_input_id', 'product_id', 'image_url')
        model = TryonOutput