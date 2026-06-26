from datetime import datetime
from database import db, ma


class ProductColor(db.Model):
    __tablename__ = 'product_colors'

    id = db.Column(db.Integer, primary_key=True)
    color_hex = db.Column(db.String)
    name = db.Column(db.String)
    name_ar = db.Column(db.String)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(
        db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProductColorSchema(ma.Schema):
    class Meta:
        fields = ('id', 'color_hex', 'name', 'name_ar',
                  'created_at', 'updated_at')
        model = ProductColor
