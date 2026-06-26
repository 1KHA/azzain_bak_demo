from database import db,ma
from datetime import datetime

class UserHeight(db.Model):
    __tablename__ = 'user_height'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,nullable=False)
    name_ar = db.Column(db.String,nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)

class UserHeightSchema(ma.Schema):
    class Meta:
        fields = ('id','name','name_ar')
        model = UserHeight