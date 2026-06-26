from database import db
from flask import g
from models.category import Category
from models.favorite import FavoriteProduct
from models.products import Products
from models.user import User,UserSchema
from models.user_age_group import UserAgeGroup,UserAgeGroupSchema
from models.user_weight import UserWeight,UserWeightSchema
from models.user_height import UserHeight,UserHeightSchema
from models.user_budget import UserBudget,UserBudgetSchema

class User_Query():

    @staticmethod
    def get_profile_data(db):
        user = g.user

        user_data = User.query.with_entities(
            User.id.label("id"),
            User.name.label("name"),
            User.phone_number.label("phone_number"),
            User.email.label("email"),
            User.active.label("active"),
            User.is_verified.label("is_verified"),
            User.country.label("country"),
            User.city.label("city"),
            User.gender.label("gender"),
            User.age_group_id.label("age_group_id"),
            User.user_budget_id.label("user_budget_id"),
            User.height_id.label("height_id"),
            User.weight_id.label("weight_id"),
            User.created_at.label("created_at"),
            User.user_metadata.label("user_metadata"),
            UserAgeGroup.name.label("age_group_name"),
            UserAgeGroup.name_ar.label("age_group_name_ar"),
            UserBudget.name.label("user_budget_name"),
            UserBudget.name_ar.label("user_budget_name_ar"),
            UserHeight.name.label("height_name"),
            UserHeight.name_ar.label("height_name_ar"),
            UserWeight.name.label("weight_name"),
            UserWeight.name_ar.label("weight_name_ar")
        ).filter(
            User.id == user.id
        ).outerjoin(
            UserAgeGroup, User.age_group_id == UserAgeGroup.id
        ).outerjoin(
            UserHeight, User.height_id == UserHeight.id
        ).outerjoin(
            UserWeight, User.weight_id == UserWeight.id
        ).outerjoin(
            UserBudget, User.user_budget_id == UserBudget.id
        ).first()

        data = UserSchema().dump(user_data)
        return data
    
    @staticmethod
    def get_preference_data(db,data,elements,user_preferences):
        response = {}

        if "body_shape" in elements:
            if user_preferences.body_shape_id:
                response["body_shape"] = user_preferences.body_shape_id
            else:
                response["body_shape"] = {}

        if "skin_tone" in elements:
            if user_preferences.skin_tone_id:
                response["skin_tone"] = user_preferences.skin_tone_id
            else:
                response["skin_tone"] = {}

        if "hair_color" in elements:
            if user_preferences.hair_color_id:
                response["hair_color"] = user_preferences.hair_color_id
            else:
                response["hair_color"] = {}

        if "body_part" in elements:
            if user_preferences.body_part_id:
                response["body_parts"] = user_preferences.body_part_id
            else:
                response["body_parts"] = []

        if "cloth_pattern" in elements:
            if user_preferences.cloth_pattern_id:
                response["cloth_pattern"] = user_preferences.cloth_pattern_id
            else:
                response["cloth_pattern"] = []

        if "cloth_color" in elements:
            if user_preferences.cloth_color_id:
                response["cloth_color"] = user_preferences.cloth_color_id
            else:
                response["cloth_color"] = []

        query = FavoriteProduct.query.with_entities(
            FavoriteProduct.id,
            Products.id
        ).join(
            Products, Products.id == FavoriteProduct.product_id
        ).join(
            Category, Category.id == Products.category_id
        )

        if "fav_topwear" in elements:
            res = query.filter(Category.name == "topwear").all()
            response["fav_topwear"] = [element.id for element in res]

        if "fav_bottomwear" in elements:
            res = query.filter(Category.name == "bottomwear").all()
            response["fav_bottomwear"] = [
                element.id for element in res]

        if "fav_footwear" in elements:
            res = query.filter(Category.name == "footwear").all()
            response["fav_footwear"] = [
                element.id for element in res]
        
        return response