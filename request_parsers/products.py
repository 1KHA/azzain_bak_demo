from pydantic import BaseModel
from typing import Optional


class LikeProductRequest(BaseModel):
    product_ids: list[int]


class CollectionCreateRequest(BaseModel):
    name: str
    name_ar: Optional[str] = None
    img_url: Optional[str] = None
    is_formal: Optional[bool] = False


class CollectionCreateResponse(BaseModel):
    collection_id: int
