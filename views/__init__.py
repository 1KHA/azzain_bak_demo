from flask import Blueprint
from flask_restx import Api
from config import Config
from models import User, BodyPart, BodyShape, ClothColor, ClothPattern, HairColor, SkinTone, UserPreference
from views.auth import auth_api
from views.user_preference import preference_api
from views.user import user_api
from views.products import products_api
from views.ai import ai_api

blueprint = Blueprint("api", "flask backend")
api = Api(blueprint, title='Apis', version='1.0', docs=Config.DEBUG)

api.add_namespace(auth_api)
api.add_namespace(preference_api)
api.add_namespace(user_api)
api.add_namespace(products_api)
api.add_namespace(ai_api)