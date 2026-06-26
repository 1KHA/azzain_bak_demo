from enum import Enum

class BaseEnum(Enum):

    @classmethod
    def values(cls):
        return cls.__members__

    @classmethod
    def get_value(cls, name):
        return cls.__getattr__(name)

class GenderEnum(BaseEnum):
    MALE = 'Male'
    FEMALE = 'Female'

class AgeGroupEnum(Enum):
    AG_12_TO_16 = '12-16'
    AG_17_TO_30 = '17-30'
    AG_31_TO_45 = '31-45'
    AG_ABOVE_45 = 'above 45'

class GenderEnumPydantic(str,Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'

class AgeGroupEnumPydantic(str,Enum):
    AG_12_TO_16 = 'AG_12_TO_16'
    AG_17_TO_30 = 'AG_17_TO_30'
    AG_31_TO_45 = 'AG_31_TO_45'
    AG_ABOVE_45 = 'AG_ABOVE_45'