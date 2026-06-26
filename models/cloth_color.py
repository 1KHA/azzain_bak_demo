from datetime import datetime
from helpers.enums import GenderEnum
from database import db, ma
from marshmallow import fields


class ClothColor(db.Model):
    __tablename__ = 'cloth_colors'

    id = db.Column(db.Integer, primary_key=True)
    combinations = db.Column(db.ARRAY(db.String))
    gender = db.Column(db.Enum(GenderEnum))    
    description = db.Column(db.String)
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)
    # def __repr__(self):
    #     return '<ClothColor {}>'.format(self.id)


class ClothColorSchema(ma.Schema):
    gender = fields.Function(lambda obj: obj.gender)

    class Meta:
        fields = ('id', 'combinations', 'gender',
                  'description', 'created_at', 'updated_at')
        model = ClothColor
