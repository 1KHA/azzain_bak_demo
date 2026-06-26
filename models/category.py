from database import db,ma 
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,nullable=False)
    name_ar = db.Column(db.String)
    img_url = db.Column(db.String)
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)

class CategorySchema(ma.Schema):
    class Meta:
        fields = ('id','name','name_ar','img_url')
        model = Category