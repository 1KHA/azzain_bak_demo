from database import db,ma 
from datetime import datetime

class SubCategory(db.Model):
    __tablename__ = 'sub_category'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,nullable=False)
    name_ar = db.Column(db.String)
    category_id = db.Column(db.Integer,db.ForeignKey('category.id'))
    img_url = db.Column(db.String)
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)

class SubCategorySchema(ma.Schema):
    class Meta:
        fields = ('id','name','name_ar','img_url')
        model = SubCategory