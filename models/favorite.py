from database import db,Marshmallow
from datetime import datetime
from marshmallow import fields

class FavoriteProduct(db.Model):
    __tablename__ = "favorite"

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer,db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)
    
    