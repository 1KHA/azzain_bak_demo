from datetime import datetime
from database import db, ma
from marshmallow import fields


class VisitedProducts(db.Model):
    __tablename__ = 'visited_products'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)


class VisitedProductsSchema(ma.Schema):
    class Meta:
        fields = ('id', 'user_id', 'product_id',
                  'product_uuid', 'created_at', 'updated_at')
        model = VisitedProducts
