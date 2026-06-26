from database import db
from logger import logger
from models import (
    UserPreference, FavoriteProduct, Products, BodyPart,
    BodyShape, SkinTone, HairColor, ClothPattern, ClothColor,
    UserAgeGroup, UserHeight, UserWeight, User, Category,
    VisitedProducts, ProductColor, ProductSize, ProductBrand,
    ProductBestFor, SubCategory,
)
from models.products import ProductSchema
from sqlalchemy.sql import column, cast, case, literal, func
from sqlalchemy import and_
from flask import g


def get_user_data(user_id: int) -> dict:
    """
    Returns the following information:
    {
        'id': user_id, 
      'country': country   ,
        'city': city,
        'age_group': age_group   ,
        'gender': gender   ,
        'height': height   ,
        'weight': weight   ,
        'body_shape': body_shape  name ,
        'skin_tone' :color name     ,
        'hair_color': color name    ,
        'cloth_patterns': name of patterns    ,
        'cloth_colors': name of colors    ,
        'body_part': list of body part names    ,
        'fav_topwear': list of product uuids  ]  ,
        'fav_bottomwear': list of product uuids ]   ,
        'fav_footwear': list of product uuids  }
    """
    user_data = {'id': user_id}
    try:
        user_res = User.query.with_entities(
            User.country,
            User.city,
            UserAgeGroup.name.label('age_group'),
            User.gender,
            UserHeight.name.label('height'),
            UserWeight.name.label('weight'),
        ).outerjoin(
            UserAgeGroup, User.age_group_id == UserAgeGroup.id
        ).outerjoin(
            UserHeight, User.height_id == UserHeight.id
        ).outerjoin(
            UserWeight, User.weight_id == UserWeight.id
        ).filter(User.id == user_id).first()

        user_data['country'] = user_res.country
        user_data['city'] = user_res.city
        user_data['age_group'] = user_res.age_group
        user_data['weight'] = user_res.weight
        user_data['height'] = user_res.height
        user_data['gender'] = user_res.gender.value

        logger.debug(user_data)

        user_preference = UserPreference.query.with_entities(
            BodyShape.name.label('body_shape'),
            SkinTone.name.label('skin_tone'),
            HairColor.name.label('hair_color'),
            UserPreference.cloth_pattern_id,
            UserPreference.cloth_color_id,
            UserPreference.body_part_id
        ).select_from(
            UserPreference
        ).outerjoin(
            BodyShape, UserPreference.body_shape_id == BodyShape.id
        ).outerjoin(
            SkinTone, UserPreference.skin_tone_id == SkinTone.id
        ).outerjoin(
            HairColor, UserPreference.hair_color_id == HairColor.id
        ).filter(
            UserPreference.user_id == user_id
        ).first()
        if user_preference.cloth_pattern_id:

            cloth_pattern_names = ClothPattern.query.with_entities(
                ClothPattern.name
            ).filter(
                ClothPattern.id.in_(user_preference.cloth_pattern_id)
            ).all()
        else:
            cloth_pattern_names = []

        if user_preference.cloth_color_id:

            color_pattern_names = ClothColor.query.with_entities(
                cast(ClothColor.combinations, db.ARRAY(
                    db.String)).label('combinations')
            ).filter(
                ClothColor.id.in_(user_preference.cloth_color_id)
            ).all()
        else:
            color_pattern_names = []

        if user_preference.body_part_id:
            body_part_names = BodyPart.query.with_entities(
                BodyPart.name
            ).filter(
                BodyPart.id.in_(user_preference.body_part_id)
            ).all()
        else:
            body_part_names = []

        user_data['body_shape'] = user_preference.body_shape
        user_data['skin_tone'] = user_preference.skin_tone
        user_data['hair_color'] = user_preference.hair_color
        user_data['cloth_patterns'] = [i.name for i in cloth_pattern_names]
        user_data['cloth_colors'] = [
            i.combinations for i in color_pattern_names]
        user_data['body_part'] = [i.name for i in body_part_names]

        logger.debug(user_data)

        fav = FavoriteProduct.query.with_entities(
            Products.product_uuid
        ).join(
            FavoriteProduct, FavoriteProduct.product_id == Products.id
        ).join(
            Category, Products.category_id == Category.id
        ).filter(
            FavoriteProduct.user_id == user_id,
        )

        fav_topwear = fav.filter(Category.name == 'topwear').all()
        fav_bottomwear = fav.filter(Category.name == 'bottomwear').all()
        fav_footwear = fav.filter(Category.name == 'footwear').all()

        user_data['fav_topwear'] = [str(i.product_uuid) for i in fav_topwear]
        user_data['fav_bottomwear'] = [
            str(i.product_uuid) for i in fav_bottomwear]
        user_data['fav_footwear'] = [str(i.product_uuid) for i in fav_footwear]

        logger.debug(user_data)

        return user_data
    except Exception as e:
        logger.error(f"Error while fetching user preference data: {e}")
        return None


def get_recently_visited_products(user_id: int) -> list[str]:
    """
        Returns the list of UUIDs of recently visited products
        of that user
    """

    try:
        visited_products = VisitedProducts.query.with_entities(
            Products.product_uuid
        ).join(
            VisitedProducts, VisitedProducts.product_id == Products.id
        ).filter(
            VisitedProducts.user_id == user_id
        ).order_by(
            VisitedProducts.created_at.desc()
        ).all()

        return [str(i.product_uuid) for i in visited_products]
    except Exception as e:
        logger.error(f"Error while fetching recently visited products: {e}")
        return None

def get_product_detail_by_uuid(product_uuid: str) -> dict:
    """
    Returns the product details of the given product_uuid
    """
    product_uuid_data = None

    color_subquery = db.session.query(
        Products.id,
        func.json_object_agg(
            ProductColor.id, ProductColor.name).label('colors_updated')
    ).join(
        ProductColor, ProductColor.id == func.any(Products.colors)
    ).group_by(
        Products.id
    ).subquery()

    size_subquery = db.session.query(
        Products.id,
        func.json_object_agg(
            ProductSize.id, ProductSize.size).label('sizes_updated')
    ).join(
        ProductSize, ProductSize.id == func.any(Products.sizes)
    ).group_by(
        Products.id
    ).subquery()

    product_uuid_data = Products.query.with_entities(
        Products.id.label('id'),
        Products.product_id.label('product_id'),
        Products.name.label('name'),
        Products.description.label('description'),
        Products.name_ar.label('label'),
        Products.description_ar.label('description_ar'),
        Products.price.label('price'),
        Products.currency.label('currency'),
        Products.link.label('link'),
        Products.sizes.label('sizes'),
        Products.view_count.label('view_count'),
        Products.best_for_id.label('best_for_id'),
        ProductBestFor.name.label('best_for_name'),
        # Products.colors.label('colors'),
        Products.image_urls.label('image_urls'),
        # Products.gender.label('gender'),
        Products.brand_id.label('brand_id'),
        ProductBrand.name.label('brand_name'),
        ProductBrand.img_url.label('brand_img_url'),
        Products.category_id.label('category_id'),
        Category.name.label('category_name'),
        Products.sub_category_id.label('sub_category_id'),
        SubCategory.name.label('sub_category_name'),
        Products.good_fit.label('good_fit'),
        Products.tryon_available.label('tryon_available'),
        Products.bg_remove_url.label('bg_remove_url'),
        case(
            (FavoriteProduct.product_id != None, literal(True)),
            else_=literal(False)
        ).label('user_favourite'),
        color_subquery.c.colors_updated.label(
            'colors'),
        size_subquery.c.sizes_updated.label(
            'sizes')
    ).outerjoin(
        FavoriteProduct,
        and_(Products.id == FavoriteProduct.product_id,
                FavoriteProduct.user_id == g.user.id)
    ).outerjoin(
        ProductBrand, Products.brand_id == ProductBrand.id
    ).outerjoin(
        Category, Products.category_id == Category.id
    ).outerjoin(
        SubCategory, Products.sub_category_id == SubCategory.id
    ).outerjoin(
        ProductBestFor, Products.best_for_id == ProductBestFor.id
    ).outerjoin(
        color_subquery, Products.id == color_subquery.c.id  # Joining the subquery here
    ).outerjoin(
        size_subquery, Products.id == size_subquery.c.id
    ).filter(Products.product_uuid == product_uuid).first()

    if product_uuid_data is None:
        return {}

    product_data = ProductSchema().dump(product_uuid_data)
    return product_data