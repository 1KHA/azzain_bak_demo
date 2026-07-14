from flask_restx import Namespace,Resource
from helpers.error_codes import error_codes
from responses import BaseResponse
from database import db
from models import User, UserPreference
from models.otp_value import OtpValue
from flask import request,g
from request_parsers.user import UserRegistrationData,UserOtpdata,UserLoginData
from helpers.pydantic_errors import get_custom_error_message
from logger import logger
from pydantic import ValidationError
from datetime import datetime,timedelta
import random
import string
from config import Config
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from models.user_age_group import UserAgeGroup
from models.user_age_group import UserAgeGroupSchema
from models.user_height import UserHeight
from models.user_height import UserHeightSchema
from models.user_weight import UserWeight
from models.user_weight import UserWeightSchema
from query.auth_query import AuthQuery
from models.user_budget import UserBudget

auth_api = Namespace('auth',description='User related operations')

# Register the User
@auth_api.route('/register')
class Register(Resource):
    def post(self):
        """
            endpoint to register a new user   
        """
        data = request.get_json()

        try:
            user = UserRegistrationData(**data)
        except ValidationError as e:
            return BaseResponse.bad_request(1011, get_custom_error_message(e))
        except Exception as e:
            return BaseResponse.bad_request(1011, str(e))

        user_exists = None

        # checking user already exist
        user_exists = AuthQuery.get_user_by_phonenumber(db,user_phone_number=data['phone_number'])

        if user_exists:
            return BaseResponse.bad_request(1004, error_codes[1004])
        
        # checking age group exist
        age_group_exists = UserAgeGroup.query.filter_by(id=user.age_group_id).first()
        if age_group_exists is None:
            return BaseResponse.bad_request(1029, error_codes[1029])
        
        # checking user budget exist
        user_budget_exist = UserBudget.query.filter_by(id=user.user_budget_id).first()
        if user_budget_exist is None:
            return BaseResponse.bad_request(1044,error_codes[1044])

        # Adding New User
        new_user = AuthQuery.add_user_to_database(db,name=user.name,country=user.country, city=user.city,age_group_id=user.age_group_id,user_budget_id=user.user_budget_id,phone_number=data['phone_number'],gender=user.gender,user_metadata=user.user_metadata)
        db.session.commit()
        # NOTE
        # create user preference so that user can update it later
        # this is also done to handle GET request for user preference
        # when user has not set any preference
        new_user_preference = AuthQuery.create_user_preference(db,user_id=new_user.id)
        db.session.commit()

        access_token = create_access_token(
            identity=new_user.id, fresh=True, expires_delta=Config.JWT_ACCESS_TOKEN_EXPIRES)

        return BaseResponse.success({
            "access_token": access_token,
        }, message="User created successfully")
    
# Send Otp To User
@auth_api.route('/send-otp')
class SendOtp(Resource):
    def post(self):
        """
        Generate an otp and send to user
        """
        data = request.get_json()
        try:
            user = UserOtpdata(**data)
        except Exception as e:
            return BaseResponse.bad_request(1011, str(e))

        user_exist = None
        # check user exist
        user_exist = AuthQuery.get_user_by_phonenumber(db,user_phone_number=data['phone_number'])

        if user_exist is None:
            return BaseResponse.bad_request(1007, error_codes[1007])
        
        # get otp value
        otp_value = AuthQuery.get_otp(db,user_id=user_exist.id)
        
        if otp_value:
            otp_value.expiry_at = datetime.utcnow()
        
        otp_code = ''.join(random.choices(string.digits, k=4))
        otp_code = '1234'
        expiry_time = datetime.utcnow() + timedelta(minutes=Config.OTP_EXPIRY_MINUTES)

        # Add otp to db
        new_otp = AuthQuery.add_opt_to_database(db,user_id=user_exist.id,code=otp_code,expiry_at=expiry_time)

        db.session.commit()

        return BaseResponse.success("Opt Send Successfully")
    
# login user
@auth_api.route('/login')
class LoginUser(Resource):
    def post(self):
        """
        login User and verify Otp
        """
        data = request.get_json()

        try:
            user = UserLoginData(**data)
        except Exception as e:
            return BaseResponse.bad_request(1011,str(e))
        
        user_exist = None
        # check user exist
        user_exist = AuthQuery.get_user_by_phonenumber(db,user_phone_number=data['phone_number'])

        if user_exist is None:
            return BaseResponse.bad_request(1007, error_codes[1007])
        
        # get otp value and verify
        otp_data = AuthQuery.get_otp_and_verify(db,user_exist_id=user_exist.id)

        if otp_data is None:
            return BaseResponse.bad_request(1009,error_codes[1009])
        
        if otp_data.code != user.otp_code:
            return BaseResponse.bad_request(1008,error_codes[1008])
        
        otp_data.is_verified = True

        db.session.commit()

        access_token = create_access_token(
            identity=user_exist.id, fresh=True, expires_delta=Config.JWT_ACCESS_TOKEN_EXPIRES)
        refresh_token = create_refresh_token(
            identity=user_exist.id, expires_delta=Config.JWT_REFRESH_TOKEN_EXPIRES)

        return BaseResponse.success({
            "access_token": access_token,
            "refresh_token": refresh_token
        }, message="User logged in successfully")

# refresh token
@auth_api.route("/refresh")
class GetRefreshToken(Resource):
    @jwt_required(refresh=True)
    def get(self):
        try:
            current_user = get_jwt_identity()
        except Exception as e:
            logger.debug("Bad Token : "+str(e))
            return BaseResponse.bad_request(1010, error_codes[1010])
        
        # create new access token
        new_token = create_access_token(identity=current_user, fresh=False)

        return BaseResponse.success({"access_token": new_token})
    
# get heights
@auth_api.route('/user-height')
class GetUserHeights(Resource):
    def get(self):
        """
        Get all user heights
        """
        heights = AuthQuery.get_all_user_heights(db)

        return BaseResponse.success(heights)

# get weights
@auth_api.route('/user-weight')
class GetUserWeights(Resource):
    def get(self):
        """
        Get all user weights
        """
        weights = AuthQuery.get_all_user_weights(db)

        return BaseResponse.success(weights)
    
# get all age groups
@auth_api.route('/user-age-group')
class GetUserAgeGroup(Resource):
    def get(self):
        """
        Get all get user age group
        """
        age_groups = AuthQuery.get_all_user_age_group(db)

        return BaseResponse.success(age_groups)
    
# get all budgets
@auth_api.route('/user-budgets')
class GetUserBudget(Resource):
    def get(self):
        """
        Get all budget
        """
        user_budgets = AuthQuery.get_all_budgets(db)

        return BaseResponse.success(user_budgets)

COUNTRIES_DATA = {
    "Saudi Arabia": ["Riyadh", "Jeddah", "Mecca", "Medina", "Dammam", "Khobar", "Dhahran", "Taif", "Tabuk", "Abha", "Khamis Mushait", "Qatif", "Jubail", "Hail", "Najran", "Yanbu", "Al Ahsa", "Buraidah"],
    "United Arab Emirates": ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain", "Al Ain"],
    "Kuwait": ["Kuwait City", "Hawalli", "Salmiya", "Farwaniya", "Ahmadi", "Jahra"],
    "Qatar": ["Doha", "Al Rayyan", "Al Wakrah", "Al Khor", "Dukhan"],
    "Bahrain": ["Manama", "Riffa", "Muharraq", "Hamad Town", "Isa Town", "Sitra"],
    "Oman": ["Muscat", "Salalah", "Sohar", "Nizwa", "Sur", "Ibri"],
    "Egypt": ["Cairo", "Alexandria", "Giza", "Shubra El Kheima", "Port Said", "Suez", "Luxor", "Aswan", "Hurghada"],
    "Jordan": ["Amman", "Zarqa", "Irbid", "Russeifa", "Aqaba", "Salt"],
    "Lebanon": ["Beirut", "Tripoli", "Sidon", "Tyre", "Jounieh"],
    "Iraq": ["Baghdad", "Basra", "Mosul", "Erbil", "Sulaymaniyah", "Najaf", "Karbala"],
    "United Kingdom": ["London", "Birmingham", "Manchester", "Leeds", "Glasgow", "Liverpool", "Bristol", "Edinburgh"],
    "United States": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"],
    "France": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Strasbourg"],
    "Germany": ["Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt", "Stuttgart", "Düsseldorf"],
    "Turkey": ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Adana", "Konya"],
    "Pakistan": ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Multan", "Peshawar"],
    "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Pune"],
    "Canada": ["Toronto", "Montreal", "Vancouver", "Calgary", "Edmonton", "Ottawa", "Winnipeg"],
    "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Gold Coast"],
}

@auth_api.route('/countries')
class GetCountries(Resource):
    def get(self):
        """
        Get list of all available countries
        """
        countries = sorted(COUNTRIES_DATA.keys())
        return BaseResponse.success(countries)

@auth_api.route('/cities')
class GetCities(Resource):
    def get(self):
        """
        Get list of cities for a given country (?country=Saudi Arabia)
        """
        country = request.args.get('country', None, type=str)

        if not country:
            return BaseResponse.bad_request(1011, "country query parameter is required")

        cities = COUNTRIES_DATA.get(country)

        if cities is None:
            return BaseResponse.not_found(1005, f"No cities found for country: {country}")

        return BaseResponse.success(sorted(cities))