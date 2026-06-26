from datetime import datetime
from database import db, ma

class CollectionName(db.Model):
    __tablename__ = 'collection_name'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,nullable=False)
    name_ar = db.Column(db.String)
    img_url = db.Column(db.String)
    is_generic = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)

class CollectionNameSchema(ma.Schema):
    class Meta:
        fields = ('id','name','name_ar', 'img_url')
        model = CollectionName