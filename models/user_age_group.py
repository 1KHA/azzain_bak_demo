from database import db,ma
from datetime import datetime

class UserAgeGroup(db.Model):
    __tablename__ = 'user_age_group'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,nullable=False)
    name_ar = db.Column(db.String,nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)

class UserAgeGroupSchema(ma.Schema):
    class Meta:
        fields = ('id','name','name_ar')
        model = UserAgeGroup