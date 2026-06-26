from datetime import datetime
from database import db, ma
from helpers.enums import GenderEnum
from marshmallow import fields
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Products(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product_uuid = db.Column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4,
        index=True)
    product_id = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    description = db.Column(db.String)
    name_ar = db.Column(db.String)
    description_ar = db.Column(db.String)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    sizes = db.Column(db.ARRAY(db.Integer))
    colors = db.Column(db.ARRAY(db.Integer))
    image_urls = db.Column(db.ARRAY(db.String))
    bg_remove_url = db.Column(db.String)
    # gender = db.Column(db.Enum(GenderEnum))
    good_fit = db.Column(db.String)
    best_for_id = db.Column(db.Integer, db.ForeignKey('product_best_for.id'))
    brand_id = db.Column(db.Integer, db.ForeignKey('product_brands.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    sub_category_id = db.Column(db.Integer, db.ForeignKey('sub_category.id'))
    tryon_available = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)


class ProductSchema(ma.Schema):
    # gender = fields.Function(
    #     lambda obj: obj.gender.value if obj.gender else None)

    class Meta:
        fields = ('id', 'product_id', 'name', 'description', 'name_ar', 'description_ar', 'price', 'currency', 'link', 'sizes', 'colors',
                  'image_urls', 'best_for_id', 'best_for_name', 'brand_id', 'brand_name','brand_img_url', 'tryon_available', 'view_count', 'category_id', 'sub_category_id', 'category_name', 'sub_category_name', 'user_favourite', 'good_fit', 'created_at', 'updated_at', 'bg_remove_url')
        model = Products


class ProductListingSchema(ma.Schema):
    # gender = fields.Function(
    #     lambda obj: obj.gender.value if obj.gender else None)
    image_url = fields.Method("get_first_image_url")
    filtered_colors = fields.Dict()

    def get_first_image_url(self, obj):
        if obj.image_urls:
            return obj.image_urls[0]
        return None

    class Meta:
        fields = ('id', 'product_id', 'name', 'description', 'name_ar', 'description_ar', 'price', 'currency', 'link', 'sizes', 'image_url', 'brand_id', 'brand_name', 'tryon_available',
                  'category_id', 'sub_category_id', 'category_name', 'sub_category_name', 'user_favourite', 'colors', 'best_for_id', 'best_for_name', 'good_fit', 'view_count', 'created_at', 'updated_at')
        model = Products
