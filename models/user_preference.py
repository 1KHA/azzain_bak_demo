from datetime import datetime
from database import db,ma
from marshmallow import fields

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    body_shape_id = db.Column(db.Integer, db.ForeignKey('body_shapes.id'))
    skin_tone_id = db.Column(db.Integer, db.ForeignKey('skin_tones.id'))
    hair_color_id = db.Column(db.Integer, db.ForeignKey('hair_colors.id'))
    cloth_pattern_id = db.Column(db.ARRAY(db.Integer))
    cloth_color_id = db.Column(db.ARRAY(db.Integer))
    body_part_id = db.Column(db.ARRAY(db.Integer))
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)
    # def __repr__(self):
    #     return '<UserPreference {}>'.format(self.id)
    
class UserPreferenceSchema(ma.Schema):
    
    class Meta:
        fields = ('id','user_id','body_shape_id','skin_tone_id','cloth_pattern_id','body_part_id','created_at', 'updated_at')
        model = UserPreference