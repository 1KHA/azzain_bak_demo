from pydantic import field_validator, BaseModel
from helpers.enums import AgeGroupEnumPydantic, GenderEnumPydantic
from typing import Optional,List,Dict
from pydantic_extra_types.phone_numbers import PhoneNumber
class UserRegistrationData(BaseModel):

    name: str
    country: str
    city: str
    age_group_id: int
    user_budget_id : int
    phone_number: PhoneNumber
    gender: GenderEnumPydantic
    user_metadata: Dict

    @field_validator('name')
    @classmethod
    def is_valid_name(cls, v):
        if len(v) == 0:
            raise Exception(
                "Name should contain atleast one character"
            )
        return v

    @field_validator('country')
    @classmethod
    def is_valid_country(cls, v):
        if len(v) == 0:
            raise Exception(
                "Country should not be empty"
            )
        return v

    # @field_validator('phone_number')
    # @classmethod
    # def is_valid_phone_number(cls, v):
    #     if v.startswith('+966'):
    #         v = v[4:]
    #     if len(v) < 9 or len(v) > 10:
    #         raise Exception(
    #             "Phone number should be 9 or 10 digits long"
    #         )
    #     if not v.isdigit():
    #         raise Exception(
    #             "Phone number should contain only digits"
    #         )

    #     return v

class UserOtpdata(BaseModel):
    
    phone_number:PhoneNumber

    # @field_validator('phone_number')
    # @classmethod
    # def is_valid_phone_number(cls, v):
    #     if v.startswith('+966'):
    #         v = v[4:]
    #     if len(v) < 9 or len(v) > 10:
    #         raise Exception(
    #             "Phone number should be 9 or 10 digits long"
    #         )
    #     if not v.isdigit():
    #         raise Exception(
    #             "Phone number should contain only digits"
    #         )
    #     return v

class UserLoginData(BaseModel):
    
    phone_number:PhoneNumber
    otp_code:str

    # @field_validator('phone_number')
    # @classmethod
    # def is_valid_phone_number(cls, v):
    #     if v.startswith('+966'):
    #         v = v[4:]
    #     if len(v) < 9 or len(v) > 10:
    #         raise Exception(
    #             "Phone number should be 9 or 10 digits long"
    #         )
    #     if not v.isdigit():
    #         raise Exception(
    #             "Phone number should contain only digits"
    #         )
    #     return v
    
    @field_validator('otp_code')
    @classmethod
    def is_otp_validator(cls,v):
        if len(v) == 0:
            raise Exception(
                "The otp field is empty"
            )
        if len(v) != 4:
            raise Exception(
                "Please Provide correct otp"
            )
        if not v.isdigit():
            raise Exception(
                "Otp should contain only digits"
            )
        return v
    
class UserUpdateData(BaseModel):

    name:Optional[str] = None
    country:Optional[str] = None
    city:Optional[str] = None
    age_group_id:Optional[int] = None
    user_budget_id:Optional[int]=None
    gender:Optional[GenderEnumPydantic] = None
    user_metadata: Optional[Dict] = None

    @field_validator('name')
    @classmethod
    def is_valid_name(cls, v):
        if len(v) == 0:
            raise Exception(
                "Name should contain atleast one character"
            )
        return v

    @field_validator('country')
    @classmethod
    def is_valid_country(cls, v):
        if len(v) == 0:
            raise Exception(
                "Country should not be empty"
            )
        return v

    @field_validator('city')
    @classmethod
    def is_valid_city(cls, v):
        if len(v) == 0:
            raise Exception(
                "City should not be empty"
            )
        return v
    
class UpdateProfilePreferenceData(BaseModel):

    body_shape:Optional[int] = None
    skin_tone:Optional[int] = None
    hair_color:Optional[int] = None
    cloth_pattern:Optional[List[int]] = None
    cloth_color:Optional[List[int]] = None
    body_part:Optional[List[int]] = None
    weight_id:Optional[int] = None
    height_id:Optional[int] = None









