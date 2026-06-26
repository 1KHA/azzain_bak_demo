from datetime import datetime
from helpers.enums import GenderEnum
from database import db,ma
from marshmallow import fields

class BodyPart(db.Model):
    __tablename__ = 'body_parts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    name_ar = db.Column(db.String)
    img_url = db.Column(db.String)
    gender = db.Column(db.Enum(GenderEnum))    
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)
    # def __repr__(self):
    #     return '<BodyPart {}>'.format(self.name)

class BodyPartSchema(ma.Schema):
    gender = fields.Function(lambda obj: obj.gender.value)
    class Meta:
        fields = ('id','name','name_ar','img_url','gender','created_at', 'updated_at')
        model = BodyPart