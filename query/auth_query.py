from database import db 
from models import User
from models import UserPreference
from models.otp_value import OtpValue
from models.user_height import UserHeight,UserHeightSchema
from models.user_weight import UserWeight,UserWeightSchema
from models.user_age_group import UserAgeGroup , UserAgeGroupSchema
from models.user_budget import UserBudget,UserBudgetSchema
from datetime import datetime
from sqlalchemy.orm import Session

class AuthQuery():
    
    @staticmethod
    def get_user_by_phonenumber(db,user_phone_number):
        print(user_phone_number)
        user_exists = User.query.filter_by(phone_number=user_phone_number).first()
        return user_exists
    
    @staticmethod
    def add_user_to_database(db,name,country,city,age_group_id,user_budget_id,phone_number,gender,user_metadata):
        new_user = User(
            name = name,
            country = country,
            city = city,
            age_group_id = age_group_id,
            user_budget_id = user_budget_id,
            phone_number = phone_number,
            gender = gender,
            user_metadata = user_metadata
        )
        db.session.add(new_user)
        return new_user

    @staticmethod
    def create_user_preference(db,user_id):
        new_user_preference = UserPreference(
            user_id = user_id
        )
        db.session.add(new_user_preference)
        return new_user_preference
    
    @staticmethod
    def get_otp(db,user_id):
        otp_value = OtpValue.query.filter(OtpValue.user_id==user_id,
                            OtpValue.expiry_at>datetime.utcnow()).first()
        return otp_value
    
    @staticmethod
    def add_opt_to_database(db,user_id,code,expiry_at):
        new_otp = OtpValue(
            user_id = user_id,
            code=code,
            expiry_at=expiry_at
        )
        db.session.add(new_otp)
        return new_otp
    
    @staticmethod
    def get_otp_and_verify(db,user_exist_id):
        otp_data = OtpValue.query.filter(
            OtpValue.user_id == user_exist_id,
            OtpValue.is_verified == False,
            OtpValue.expiry_at > datetime.utcnow()
        ).first()
        return otp_data
    
    @staticmethod
    def get_all_user_heights(db):
        user_heights = UserHeight.query.all()
        heights = UserHeightSchema(many=True).dump(user_heights)
        return heights
    
    @staticmethod
    def get_all_user_weights(db):
        user_weights = UserWeight.query.all()
        weights = UserWeightSchema(many=True).dump(user_weights)
        return weights
    
    @staticmethod
    def get_all_user_age_group(db):
        user_age_groups = UserAgeGroup.query.all()
        age_groups = UserAgeGroupSchema(many=True).dump(user_age_groups)
        return age_groups
    
    @staticmethod
    def get_all_budgets(db):
        user_budgets = UserBudget.query.all()
        budgets = UserBudgetSchema(many=True).dump(user_budgets)
        return budgets
