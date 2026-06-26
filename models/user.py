from database import db, ma
from datetime import datetime
from marshmallow import fields
from helpers.enums import GenderEnum, AgeGroupEnum


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    password = db.Column(db.LargeBinary)
    active = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean)
    country = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    gender = db.Column(db.Enum(GenderEnum))
    age_group_id = db.Column(db.Integer, db.ForeignKey('user_age_group.id'))
    user_budget_id = db.Column(db.Integer,db.ForeignKey('user_budget.id'))
    height_id = db.Column(db.Integer, db.ForeignKey('user_height.id'))
    weight_id = db.Column(db.Integer, db.ForeignKey('user_weight.id'))
    user_metadata = db.Column(db.JSON)
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)

    # def __repr__(self):
    #     return '<User {}>'.format(self.name)

class UserSchema(ma.Schema):
    gender = fields.Function(lambda obj: obj.gender.value)
    # age_group = fields.Function(lambda obj: obj.age_group.value)

    class Meta:
        fields = ('id', 'name', 'phone_number', 'email', 'active', 'is_verified', 'country',
                  'city', 'gender', 'age_group_id','user_budget_id','user_budget_name','user_budget_name_ar', 'age_group_name', 'age_group_name_ar',
                  'height_id', 'height_name', 'height_name_ar', 'weight_id', 'weight_name','user_metadata','weight_name_ar', 'created_at')
        model = User
