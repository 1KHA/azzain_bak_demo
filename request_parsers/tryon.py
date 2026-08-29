from pydantic import BaseModel, field_validator


from typing import Optional

CANONICAL_GARMENTS = {
    "upper-body": "Upper-body",
    "lower-body": "Lower-body",
    "dress": "Dress",
}


class OOTDModelRequestBody(BaseModel):
    product_id: int
    user_tryon_input_id: int
    # Advisory only — the endpoint derives the garment class from the
    # product's category. Matched case-insensitively because the shipped app
    # sends "dress" for dresses, which used to be rejected outright.
    garment_type: Optional[str] = None

    @field_validator("garment_type")
    def validate_garment_type(cls, value):
        if value is None:
            return None
        canonical = CANONICAL_GARMENTS.get(str(value).strip().lower())
        if canonical is None:
            raise ValueError("Invalid garment type")

        return canonical
