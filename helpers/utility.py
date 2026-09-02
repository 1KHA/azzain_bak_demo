from database import db
from models import (
    Products, ProductBrand, ProductColor, ProductSize,
    Category, SubCategory, ProductBestFor,CollectionName,CollectionItems
)
import json
import os
from logger import logger
from sqlalchemy import func, text
from helpers.styles import classify_style, style_for_collection
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


# Which product categories may fill each board slot. Resolved by NAME because
# category ids differ between the dev seed and the demo server.
SLOT_CATEGORIES = {
    "topwear": ["topwear", "outwear"],   # a jacket/coat is a valid hero piece
    "bottom_wear": ["bottomwear"],
    "foot_wear": ["footwear"],
    "accessories": ["accesories"],       # the table really is spelled this way
}
BOARD_GENDERS = ("men", "women")
BOARDS_PER_GENDER = 5
# Fixed seed: re-running the seeder reproduces the same lookbook.
BOARD_SEED = 20260828


def _style_choices(pool, used, style):
    """Unused products for a slot, preferring the collection's own style.

    Every collection tab (Casual/Formal/Sporty/Trendy) draws from its own
    style bucket first — that is what makes the tabs actually different.
    If the bucket runs dry, fall back to casual basics, then to anything,
    so a board is never left with an empty slot.
    """
    unused = [p for p in pool if p.product_uuid not in used]
    if style:
        styled = [p for p in unused if classify_style(p.name) == style]
        if styled:
            return styled
        neutral = [p for p in unused if classify_style(p.name) == "casual"]
        if neutral:
            return neutral
    return unused


def _slot_pool(slot, gender, demo_only):
    """Board-eligible products for one slot and gender.

    Eligibility follows the boards spec: right category for the slot, a real
    gender tag (the product's own gender or unisex — never child/Other/NULL),
    and at least one image so no tile renders empty.
    """
    query = (
        Products.query
        .join(Category, Products.category_id == Category.id)
        .join(ProductBestFor, Products.best_for_id == ProductBestFor.id)
        .filter(Category.name.in_(SLOT_CATEGORIES[slot]),
                ProductBestFor.name.in_([gender, "unisex"]),
                Products.image_urls.isnot(None),
                func.array_length(Products.image_urls, 1) > 0)
    )
    if demo_only:
        # demo build: only products whose images are served locally.
        # image_urls_original is created by prepare_demo.py and kept off the
        # model on purpose, so it is referenced as raw SQL here.
        query = query.filter(text("products.image_urls_original IS NOT NULL"))
    return query.order_by(Products.id.asc()).all()


def pick_accessory(gender, exclude=None):
    """One board-eligible accessory for this gender, or None if there is none."""
    pool = [p for p in _slot_pool("accessories", gender,
                                  os.getenv("DEMO_MODE") == "1")
            if p.product_uuid not in (exclude or set())]
    return random.choice(pool) if pool else None


def insert_collection_item_in_db(demo_only=None):
    """Build 'Made for you' outfit boards: every collection x gender.

    Each board carries all four slots, filled with products of the matching
    gender and the correct category, and no product repeats inside one
    collection so the lookbook does not feel duplicated.
    """
    if demo_only is None:
        demo_only = os.getenv("DEMO_MODE") == "1"

    # Template collections only — boards a user built for themselves are left
    # untouched.
    collections = (CollectionName.query
                   .filter(CollectionName.user_id.is_(None))
                   .order_by(CollectionName.id).all())
    ids = [c.id for c in collections]
    if ids:
        CollectionItems.query.filter(
            CollectionItems.collection_id.in_(ids)).delete(
                synchronize_session=False)

    rng = random.Random(BOARD_SEED)
    created = skipped = 0

    for collection in collections:
        style = style_for_collection(collection.name)
        formal = style == "formal"
        for gender in BOARD_GENDERS:
            pools = {slot: _slot_pool(slot, gender, demo_only)
                     for slot in SLOT_CATEGORIES}
            used = set()          # no product twice within one collection

            for _ in range(BOARDS_PER_GENDER):
                board = {}
                for slot in ("topwear", "bottom_wear", "foot_wear", "accessories"):
                    choices = _style_choices(pools[slot], used, style)
                    if not choices:
                        board = None
                        break
                    pick = rng.choice(choices)
                    used.add(pick.product_uuid)
                    board[slot] = pick

                if not board:
                    skipped += 1
                    continue

                db.session.add(CollectionItems(
                    collection_id=collection.id,
                    gender=gender,
                    topwear_uuid=board["topwear"].product_uuid,
                    bottom_wear_uuid=board["bottom_wear"].product_uuid,
                    foot_wear_uuid=board["foot_wear"].product_uuid,
                    accessories_uuid=board["accessories"].product_uuid,
                    formal=formal,
                    price=int(sum(p.price or 0 for p in board.values())),
                    currency="SAR",
                ))
                created += 1

    db.session.commit()
    logger.debug(f"Collection boards inserted: {created} created, "
                 f"{skipped} skipped for lack of eligible products")
    return created, skipped
