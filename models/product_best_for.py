from database import db, ma
from datetime import datetime


class ProductBestFor(db.Model):
    __tablename__ = 'product_best_for'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    name_ar = db.Column(db.String)

    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)


class ProductBestForSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'name_ar')
        model = ProductBestFor