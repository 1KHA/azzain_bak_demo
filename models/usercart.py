from database import db,ma 
from datetime import datetime
from marshmallow import fields

class UserCart(db.Model):
    __tablename__ = 'user_cart'

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer,db.ForeignKey('products.id'),nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)

class UserCartSchema(ma.Schema):
    gender = fields.Function(lambda obj: obj.gender if obj.gender else None)
    
    class Meta:
        fields = ('id','user_id','product_id','product_name','product_description','product_name_ar','product_description_ar','price','currency','link','sizes','colors','image_url','gender','brand_id','category_id','sub_category_id','tryon_available')
        model = UserCart
