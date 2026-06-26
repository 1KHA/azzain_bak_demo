from database import db
from models.body_shape import BodyShape,BodyShapeSchema
from models.skin_tone import SkinTone,SkinToneSchema
from models.hair_color import HairColor,HairColorSchema

class User_Preference_Query():

    @staticmethod
    def get_all_body_shapes(db,gender):
        body_shape_data = BodyShape.query

        if gender:
            body_shape_data = body_shape_data.filter(
                BodyShape.gender == gender).all()
        else:
            body_shape_data = body_shape_data.all()

        body_shape = BodyShapeSchema(many=True).dump(body_shape_data)
        return body_shape
    
    @staticmethod
    def get_all_skin_tones(db):
        skin_tone_data = SkinTone.query.all()
        skin_data = SkinToneSchema(many=True).dump(skin_tone_data)
        return skin_data
    
    @staticmethod
    def get_all_hair_color(db):
        hair_color_data = HairColor.query.all()
        hair_data = HairColorSchema(many=True).dump(hair_color_data)
        return hair_data
