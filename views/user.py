from flask_restx import Namespace, Resource
from helpers.error_codes import error_codes
from responses import BaseResponse
from database import db
from models import User
from flask import request, g
from config import Config
from models.user import UserSchema
from helpers.auth import login_required
from request_parsers.user import UserUpdateData, UpdateProfilePreferenceData
from models.user_preference import UserPreference, UserPreferenceSchema
from models.body_part import BodyPart, BodyPartSchema
from models.body_shape import BodyShape, BodyShapeSchema
from models.skin_tone import SkinTone, SkinToneSchema
from models.cloth_pattern import ClothPattern, ClothPatternSchema
from models.cloth_color import ClothColor, ClothColorSchema
from models.hair_color import HairColor, HairColorSchema
from models.user_age_group import UserAgeGroup, UserAgeGroupSchema
from models.user_height import UserHeight, UserHeightSchema
from models.user_weight import UserWeight, UserWeightSchema
from models.user_tryon_input import UserTryonInput, UserTryonInputSchema
from models.user_budget import UserBudget,UserBudgetSchema
from models import Products, FavoriteProduct, Category
from datetime import datetime
from pydantic import ValidationError
from helpers.aws_bucket import upload_obj_to_s3
from helpers.pydantic_errors import get_custom_error_message
import random
import os
from tryon.remove_background import remove_background
from logger import logger
from query.user_query import User_Query

user_api = Namespace('user', description='User related operations')

# Get user profile data and set user preference data
@user_api.route('/profile')
class GetProfileData(Resource):
    @login_required
    def get(self):
        """
        Get user profile data
        """
        data = User_Query.get_profile_data(db)
        return BaseResponse.success(data)

    @login_required
    def put(self):
        """
        Update User profile data
        """

        data = request.get_json()

        try:
            data = UserUpdateData(**data)
        except ValidationError as e:
            return BaseResponse.bad_request(1011, get_custom_error_message(e))
        except Exception as e:
            return BaseResponse.bad_request(1011, str(e))

        user = g.user

        user_data = User.query.filter_by(id=user.id).first()

        if data.name:
            user_data.name = data.name
        if data.country:
            user_data.country = data.country
        if data.city:
            user_data.city = data.city
        if data.age_group_id:
            age_group_exists = UserAgeGroup.query.filter_by(
                id=data.age_group_id).first()
            if age_group_exists is None:
                return BaseResponse.bad_request(1029, error_codes[1029])
            user_data.age_group_id = data.age_group_id
        if data.user_budget_id:
            user_budget_exist = UserBudget.query.filter_by(
                id=data.user_budget_id
            ).first()
            if user_budget_exist is None:
                return BaseResponse.bad_request(1044,error_codes[1044])
            user_data.user_budget_id = data.user_budget_id
        if data.gender:
            user_data.gender = data.gender
        if data.user_metadata:
            user_data.user_metadata = data.user_metadata
    
        user_data.updated_at = datetime.utcnow()

        db.session.commit()

        return BaseResponse.success(
            data="User profile updated successfully")

# Get user preference data
@user_api.route('/profile/preference')
class GetProfilePreferenceData(Resource):
    @login_required
    def get(self):

        data = request.args.get('params', None, type=str)

        if data:
            elements = [element.strip() for element in data.split(',')]

        allowed_values = ["body_shape", "skin_tone", "hair_color",
                          "cloth_pattern", "cloth_color", "body_part",
                          "fav_topwear", "fav_bottomwear", "fav_footwear"]

        for element in elements:
            if element not in allowed_values:
                return BaseResponse.bad_request(1013, error_codes[1013])

        user = g.user

        user_preferences = UserPreference.query.filter_by(
            user_id=user.id).first()

        response = User_Query.get_preference_data(db,data,elements,user_preferences)

        return BaseResponse.success(response)

    @login_required
    def put(self):
        """
        Update user preference Table
        """

        data = request.get_json()

        try:
            data = UpdateProfilePreferenceData(**data)
        except Exception as e:
            return BaseResponse.bad_request(1011, str(e))

        if data.height_id:
            height_id_exists = UserHeight.query.filter_by(
                id=data.height_id).first()
            if height_id_exists is None:
                return BaseResponse.bad_request(1030, error_codes[1030])

        if data.weight_id:
            weight_id_exists = UserWeight.query.filter_by(
                id=data.weight_id).first()
            if weight_id_exists is None:
                return BaseResponse.bad_request(1031, error_codes[1031])

        if data.body_shape:
            body_shape_data = None
            body_shape_data = BodyShape.query.filter_by(
                id=data.body_shape).first()
            if body_shape_data is None:
                return BaseResponse.bad_request(1015, error_codes[1015])

        if data.skin_tone:
            skin_tone_data = None
            skin_tone_data = SkinTone.query.filter_by(
                id=data.skin_tone).first()
            if skin_tone_data is None:
                return BaseResponse.bad_request(1016, error_codes[1016])

        if data.hair_color:
            hair_color_data = None
            hair_color_data = HairColor.query.filter_by(
                id=data.hair_color).first()
            if hair_color_data is None:
                return BaseResponse.bad_request(1017, error_codes[1017])

        if data.cloth_pattern:
            for element in data.cloth_pattern:
                cloth_pattern_data = None
                cloth_pattern_data = ClothPattern.query.filter_by(
                    id=element).first()
                if cloth_pattern_data is None:
                    return BaseResponse.bad_request(1018, error_codes[1018])

        if data.cloth_color:
            for element in data.cloth_color:
                cloth_color_data = None
                cloth_color_data = ClothColor.query.filter_by(
                    id=element).first()
                if cloth_color_data is None:
                    return BaseResponse.bad_request(1019, error_codes[1019])

        if data.body_part:
            for element in data.body_part:
                body_part_data = None
                body_part_data = BodyPart.query.filter_by(id=element).first()
                if body_part_data is None:
                    return BaseResponse.bad_request(1020, error_codes[1020])

        user = g.user

        user_data_preference = None

        user_data_preference = UserPreference.query.filter_by(
            user_id=user.id).first()
        user_data = User.query.filter_by(id=user.id).first()

        if user_data_preference is None:
            new_preference = UserPreference(
                user_id=user.id,
                body_shape_id=data.body_shape,
                skin_tone_id=data.skin_tone,
                hair_color_id=data.hair_color,
                cloth_pattern_id=data.cloth_pattern,
                cloth_color_id=data.cloth_color,
                body_part_id=data.body_part,
            )
            if data.height_id:
                user_data.height_id = data.height_id
            if data.weight_id:
                user_data.weight_id = data.weight_id
            db.session.add(new_preference)
            db.session.commit()
            return BaseResponse.success("User preferences updated successfully.")

        if data.body_shape:
            user_data_preference.body_shape_id = data.body_shape
        if data.skin_tone:
            user_data_preference.skin_tone_id = data.skin_tone
        if data.hair_color:
            user_data_preference.hair_color_id = data.hair_color
        if data.cloth_pattern:
            user_data_preference.cloth_pattern_id = data.cloth_pattern
        if data.cloth_color:
            user_data_preference.cloth_color_id = data.cloth_color
        if data.body_part:
            user_data_preference.body_part_id = data.body_part
        if data.height_id:
            user_data.height_id = data.height_id
        if data.weight_id:
            user_data.weight_id = data.weight_id

        user_data.updated_at = datetime.utcnow()

        db.session.commit()

        return BaseResponse.success("User preferences updated successfully.")

# get all heights
@user_api.route('/user-height')
class GetUserHeights(Resource):
    def get(self):
        """
        Get all user heights
        """
        user_heights = UserHeight.query.all()

        heights = UserHeightSchema(many=True).dump(user_heights)

        return BaseResponse.success(heights)

# get all weights
@user_api.route('/user-weight')
class GetUserWeights(Resource):
    def get(self):
        """
        Get all user weights
        """
        user_weights = UserWeight.query.all()

        weights = UserWeightSchema(many=True).dump(user_weights)

        return BaseResponse.success(weights)

# get all age groups
@user_api.route('/user-age-group')
class GetUserAgeGroup(Resource):
    def get(self):
        """
        Get all get user age group
        """
        user_age_groups = UserAgeGroup.query.all()

        age_groups = UserAgeGroupSchema(many=True).dump(user_age_groups)

        return BaseResponse.success(age_groups)

# upload user picture
@user_api.route('/upload-tryon-input')
class UploadUserPicture(Resource):
    @login_required
    def post(self):
        """
        Upload user picture
        """
        user = g.user

        if "file" not in request.files:
            return BaseResponse.bad_request(1037, error_codes[1037])

        file = request.files['file']
        if file.filename == '':
            return BaseResponse.bad_request(1038, error_codes[1038])

        if file.mimetype not in ['image/jpeg', 'image/png', 'image/jpg', 'image/gif']:
            return BaseResponse.bad_request(1039, error_codes[1039])

        file_extension = file.filename.split('.')[-1]
        tmp_filename = random.randbytes(16).hex() + '.' + file_extension

        # run the remove background model
        file.save(f"./tmp/input/{tmp_filename}")
        try:
            logger.debug("Running background removal model")
            output_image_path = remove_background(
                f"./tmp/input/{tmp_filename}")
        except Exception as e:
            os.remove(f"./tmp/input/{tmp_filename}")
            logger.error(f"Error while removing background:\n {e}")
            return BaseResponse.internal_server_error(1035, error_codes[1035])

        file_obj = open(output_image_path, 'rb')
        bucket_path = "images/products/try_on/input/human"
        s3_filename = output_image_path.split("/")[-1]
        upload_status = upload_obj_to_s3(
            file=file_obj,
            file_name=s3_filename,
            bucket_path=bucket_path
        )
        if not upload_status:
            return BaseResponse.bad_request(1040, error_codes[1040])

        os.remove(output_image_path)
        os.remove(f"./tmp/input/{tmp_filename}")

        s3_image_url = f"{Config.AWS_S3_BUCKET_URL}/{bucket_path}/{s3_filename}"
        new_user_tryon_input = UserTryonInput(
            user_id=user.id,
            image_url=s3_image_url
        )

        db.session.add(new_user_tryon_input)
        db.session.commit()

        return BaseResponse.success({
            "user_tryon_input_id": new_user_tryon_input.id,
            "image_url": s3_image_url
        }, "image uploaded successfully")
