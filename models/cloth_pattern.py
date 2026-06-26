from datetime import datetime
from helpers.enums import GenderEnum
from database import db,ma
from marshmallow import fields

class ClothPattern(db.Model):
    __tablename__ = 'cloth_patterns'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    gender = db.Column(db.Enum(GenderEnum))
    description = db.Column(db.Text)
    img_url = db.Column(db.String, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)
    # def __repr__(self):
    #     return '<ClothPattern {}>'.format(self.name)

class ClothPatternSchema(ma.Schema):
    gender = fields.Function(lambda obj: obj.gender.value)
    class Meta:
        fields = ('id','name','img_url','gender','description','created_at', 'updated_at')
        model = ClothPattern