from database import db
from models import (
    Products, ProductBrand, ProductColor, ProductSize,
    Category, SubCategory, ProductBestFor,CollectionName,CollectionItems
)
import json
from logger import logger
import pandas as pd
import uuid
import random

def insert_products_in_db():

    def get_product_by_id(data, product_id: str) -> (dict | None):
        for product in data:
            if product['product_id'].lower() == product_id.lower():
                return product
        return None
    product_brands = {}
    product_sizes = {}
    product_colors = {}
    product_categories = {}
    product_sub_categories = {}
    product_bestfor = {}

    # ----------------- BRANDS -----------------
    with open('PRODUCT_BRANDS.json') as f:
        data = json.load(f)
        for brand in data:
            product_brands[brand['brand'].upper()] = brand['id']
            brand_obj = ProductBrand(
                id=brand['id'],
                name=brand['brand']
            )
            db.session.add(brand_obj)

    logger.debug("Brands inserted successfully")

    # ----------------- SIZES -----------------
    with open('PRODUCT_SIZES.json') as f:
        data = json.load(f)
        for size in data:
            product_sizes[size['size'].upper()] = size['id']
            size_obj = ProductSize(
                id=size['id'],
                size=size['size']
            )
            db.session.add(size_obj)

    logger.debug("Sizes inserted successfully")

    # ----------------- COLORS -----------------
    with open('PRODUCT_COLORS.json') as f:
        data = json.load(f)
        for color in data:
            product_colors[color['color'].upper()] = color['id']
            color_obj = ProductColor(
                id=color['id'],
                name=color['color']
            )
            db.session.add(color_obj)

    logger.debug("Colors inserted successfully")
    db.session.commit()

    df = pd.read_csv('All_PRODUCTS.csv')

    # ----------------- CATEGORIES -----------------
    for category in df['Category'].unique():
        product_categories[category.upper()] = len(product_categories)+1

        category_obj = Category(
            id=product_categories[category.upper()],
            name=category
        )
        db.session.add(category_obj)

    logger.debug("Categories inserted successfully")
    db.session.commit()

    # ----------------- SUB CATEGORIES -----------------
    for sub_category in df['Sub-Category'].unique():
        product_sub_categories[sub_category.upper()] = len(
            product_sub_categories)+1

        sub_category_obj = SubCategory(
            id=product_sub_categories[sub_category.upper()],
            name=sub_category
        )
        db.session.add(sub_category_obj)

    logger.debug("Sub Categories inserted successfully")
    db.session.commit()

    # ----------------- BEST FOR -----------------
    for best_for in df['Best-For'].unique():
        product_bestfor[best_for.upper()] = len(product_bestfor)+1

        best_for_obj = ProductBestFor(
            id=product_bestfor[best_for.upper()],
            name=best_for
        )
        db.session.add(best_for_obj)

    # insert an extra Other best for
    product_bestfor['OTHER'] = len(product_bestfor)+1
    best_for_obj = ProductBestFor(
        id=product_bestfor['OTHER'],
        name='Other'
    )
    db.session.add(best_for_obj)

    logger.debug("Best For inserted successfully")
    db.session.commit()
    unique_ids = []
    # ----------------- PRODUCTS -----------------
    with open('ALL_PRODUCTS.json') as f:
        product_json_data = json.load(f)

    for i in range(len(df)):
        if df['product_id'][i].upper() in unique_ids:
            continue
        unique_ids.append(df['product_id'][i].upper())
        try:
            product_obj_from_json = get_product_by_id(
                product_json_data, df['product_id'][i])
            good_fit_value = eval(df['Good-Fit'][i])
            if None in good_fit_value:
                good_fit_value = ""
            else:
                good_fit_value = '\n'.join(good_fit_value)
            product_obj = Products(
                product_id=df['product_id'][i],
                product_uuid=uuid.uuid4(),
                name=None if pd.isnull(df['title'][i]) else df['title'][i],
                description=None if pd.isnull(df['description'][i]) else df['description'][i],
                name_ar=None if pd.isnull(df['title_ar'][i]) else df['title_ar'][i],
                description_ar=None if pd.isnull(df['description_ar'][i]) else df['description_ar'][i],
                currency=product_obj_from_json['currency'],
                price=product_obj_from_json['price'],
                link=df['link'][i],
                sizes=[product_sizes[size.upper()]
                    for size in eval(df['sizes'][i])],
                colors=[product_colors[color.upper()]
                        for color in eval(df['colors'][i])],
                image_urls=eval(df['image_urls'][i]),
                good_fit=good_fit_value,
                best_for_id=product_bestfor[df['Best-For'][i].upper()],
                brand_id=product_brands[df['brand'][i].upper()],
                category_id=product_categories[df['Category'][i].upper()],
                sub_category_id=product_sub_categories[df['Sub-Category'][i].upper()],
                tryon_available=df['tryon_available'][i],
            )
            db.session.add(product_obj)
        except Exception as e:
            logger.error("Error while inserting product: ")
            logger.debug(f"{df['product_id'][i]}: {e}")

    logger.debug("Products inserted successfully")
    db.session.commit()

    # with open('ALL_PRODUCTS.json') as f:
    #     data = json.load(f)
    #     for product in data:
    #         product_obj = Products(
    #             product_id=product['product_id'],
    #             name=product['title'],
    #             description=product['description'],
    #             name_ar=product['title_ar'],
    #             description_ar=product['description_ar'],
    #             currency=product['currency'],
    #             price=product['price'],
    #             link=product['link'],
    #             sizes=product['size_ids'],
    #             colors=product['color_ids'],
    #             image_urls=product['image_urls'],
    #             gender=product['gender'].upper() if len(
    #                 product['gender']) > 0 else None,
    #             brand_id=product['brand_id'],
    #             # category=product['category'],
    #             tryon_available=product['tryon_available']
    #         )
    #         db.session.add(product_obj)


def insert_collections_in_db():
    
    with open('COLLECTION_NAME.json') as f:
        data = json.load(f)
        for item in data:
            collection_obj = CollectionName(
                id=item['id'],
                name=item['name']
            )
            db.session.add(collection_obj)

    logger.debug("Collection_Names inserted successfully")
    db.session.commit()


def insert_collection_item_in_db():

    top_wear_dataset = Products.query.filter_by(category_id = 2).all()
    bottom_wear_dataset = Products.query.filter_by(category_id = 3).all()
    foot_wear_dataset = Products.query.filter_by(category_id = 6).all()
    accesories_dataset = Products.query.filter_by(category_id = 4).all()
    collection_data = CollectionName.query.all()

    for i in range(30):
        top_wear_uuid = random.choice(top_wear_dataset).product_uuid
        bottom_wear_uuid = random.choice(bottom_wear_dataset).product_uuid
        foot_wear_uuid = random.choice(foot_wear_dataset).product_uuid
        accesories_uuid = random.choice(accesories_dataset).product_uuid
        collection_id = random.choice(collection_data).id

        collection_item_obj = CollectionItems(
            collection_id = collection_id,
            topwear_uuid = top_wear_uuid,
            bottom_wear_uuid = bottom_wear_uuid,
            foot_wear_uuid = foot_wear_uuid,
            accessories_uuid = accesories_uuid
        )
        db.session.add(collection_item_obj)
        logger.debug("added")

    logger.debug("Collection Items inserted successfully")
    db.session.commit()
