from pydantic import BaseModel, field_validator


class OOTDModelRequestBody(BaseModel):
    product_id: int
    user_tryon_input_id: int
    garment_type: str

    @field_validator("garment_type")
    def validate_garment_type(cls, value):
        if value not in ["Upper-body", "Lower-body", "Dress"]:
            raise Exception("Invalid garment type")

        return value
