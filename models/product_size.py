from datetime import datetime
from database import db,ma

class ProductSize(db.Model):
    __tablename__ = 'product_sizes'

    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(
        db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProductSizeSchema(ma.Schema):
    class Meta:
        fields = ('id','size','created_at','updated_at')
        model = ProductSize