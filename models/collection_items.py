from datetime import datetime
from database import db,ma
from sqlalchemy.dialects.postgresql import UUID

class CollectionItems(db.Model):
    __tablename__ = 'collection_items'

    id = db.Column(db.Integer,primary_key=True)
    collection_id = db.Column(db.Integer,db.ForeignKey('collection_name.id'))
    topwear_uuid = db.Column(UUID(as_uuid=True),db.ForeignKey('products.product_uuid'))
    bottom_wear_uuid = db.Column(UUID(as_uuid=True),db.ForeignKey('products.product_uuid'))
    foot_wear_uuid = db.Column(UUID(as_uuid=True),db.ForeignKey('products.product_uuid'))
    accessories_uuid = db.Column(UUID(as_uuid=True),db.ForeignKey('products.product_uuid'))
    price = db.Column(db.Integer)
    currency = db.Column(db.String)
    formal = db.Column(db.Boolean,default=False)
    # 'men' | 'women' | 'unisex' — every garment on the board matches it,
    # so boards can be filtered for the logged-in user without four joins.
    gender = db.Column(db.String(10), nullable=False,
                       server_default='unisex', default='unisex')
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)
    
class CollectionItemsSchema(ma.Schema):
    class Meta:
        fields = ('id','collection_id','topwear_uuid','bottom_wear_uuid','foot_wear_uuid','accessories_uuid', 'formal', 'currency', 'price', 'gender')
        model = CollectionItems