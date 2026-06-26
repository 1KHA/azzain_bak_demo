from flask_restx import Namespace, Resource
from helpers.error_codes import error_codes
from responses import BaseResponse
from database import db
from models import UserPreference, BodyPart, BodyShape, SkinTone, HairColor, ClothPattern, ClothColor
from flask import request, g
from models.body_part import BodyPartSchema
from models.cloth_color import ClothColorSchema
from models.cloth_pattern import ClothPatternSchema
from models.hair_color import HairColorSchema
from models.body_shape import BodyShapeSchema
from models.skin_tone import SkinToneSchema
from logger import logger
from query.user_preference_query import User_Preference_Query

preference_api = Namespace(
    'user-preference', description='Preference of a user')

# get all body shapes
@preference_api.route('/body-shape')
class BodyPartData(Resource):
    def get(self):
        """
        endpoint to return all the body shapes 
        """
        gender = request.args.get('gender', None, type=str)

        if gender is not None:
            gender = gender.upper()
            if gender not in ['MALE', 'FEMALE']:
                return BaseResponse.bad_request(1006, error_codes[1006])

        body_shape = User_Preference_Query.get_all_body_shapes(db,gender)

        if len(body_shape) == 0:
            return BaseResponse.not_found(1005, error_codes[1005])

        return BaseResponse.success(body_shape)

# get all skin tones
@preference_api.route('/skin-tone')
class SkinToneData(Resource):
    def get(self):
        """
        endpoint to return all the skin tones
        """
        skin_data = User_Preference_Query.get_all_skin_tones(db)

        if len(skin_data) == 0:
            return BaseResponse.not_found(1005, error_codes[1005])
        return BaseResponse.success(skin_data)

# get all hair colors
@preference_api.route('/hair-color')
class HairColorData(Resource):
    def get(self):
        """
        endpoint to return all the hair color 
        """
        hair_data = User_Preference_Query.get_all_hair_color(db)
 
        if len(hair_data) == 0:
            return BaseResponse.not_found(1005, error_codes[1005])

        return BaseResponse.success(hair_data)

# get all cloth patterns
@preference_api.route('/cloth-pattern')
class ClothPatternData(Resource):
    def get(self):
        """
        endpoint to return all the cloth pattern
        """

        gender = request.args.get('gender', None, type=str)

        if gender is not None:
            gender = gender.upper()
            if gender not in ['MALE', 'FEMALE']:
                return BaseResponse.bad_request(1006, error_codes[1006])

        if gender:
            cloth_pattern_data = ClothPattern.query.filter(
                ClothPattern.gender == gender).all()
        else:
            cloth_pattern_data = ClothPattern.query.all()

        pattern_data = ClothPatternSchema(many=True).dump(cloth_pattern_data)

        if len(pattern_data) == 0:
            return BaseResponse.not_found(1005, error_codes[1005])

        return BaseResponse.success(pattern_data)

# get all cloth color
@preference_api.route('/cloth-color')
class ColorClothData(Resource):
    def get(self):
        """
        endpoint to return all the cloth color
        """
        color_cloth_data = ClothColor.query.all()

        cloth_data = ClothColorSchema(many=True).dump(color_cloth_data)

        if len(cloth_data) == 0:
            return BaseResponse.not_found(1005, error_codes[1005])

        return BaseResponse.success(cloth_data)

# get all body parts
@preference_api.route('/body-part')
class BodyPartData(Resource):
    def get(self):
        """
        endpoint to return all the body shapes 
        """
        gender = request.args.get('gender', 'male', type=str)

        if gender is not None:
            gender = gender.upper()
            if gender not in ['MALE', 'FEMALE']:
                return BaseResponse.bad_request(1006, error_codes[1006])

        body_part_data = BodyPart.query
        if gender:
            body_part_data = body_part_data.filter(
                BodyPart.gender == gender).all()
        else:
            body_part_data = body_part_data.all()

        body_part = BodyPartSchema(many=True).dump(body_part_data)

        if len(body_part) == 0:
            return BaseResponse.not_found(1005, error_codes[1005])

        return BaseResponse.success(body_part)
