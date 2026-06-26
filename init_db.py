from database import db
from models import *
import pandas as pd
from logger import logger


def fetch_data_to_csv():
    def fetch_and_save(model, filename):
        data = db.session.query(model).all()
        data_dict = [item.__dict__ for item in data]
        for item in data_dict:
            item.pop("_sa_instance_state", None)  # Remove SQLAlchemy instance state
        df = pd.DataFrame(data_dict)
        df.to_csv(filename, index=False)
        logger.info(f"{filename} saved with {len(df)} records")

    fetch_and_save(Banner, "db_export/banners.csv")
    fetch_and_save(BodyPart, "db_export/body_parts.csv")
    fetch_and_save(BodyShape, "db_export/body_shapes.csv")
    fetch_and_save(UserAgeGroup, "db_export/user_age_group.csv")
    fetch_and_save(UserHeight, "db_export/user_height.csv")
    fetch_and_save(UserWeight, "db_export/user_weight.csv")
    fetch_and_save(UserBudget, "db_export/user_budget.csv")
    fetch_and_save(ClothColor, "db_export/cloth_colors.csv")
    # fetch_and_save(ClothPattern, "db_export/cloth_patterns.csv") # Uncomment when ClothPattern model is available
    fetch_and_save(HairColor, "db_export/hair_colors.csv")
    fetch_and_save(SkinTone, "db_export/skin_tones.csv")
    fetch_and_save(Category, "db_export/category.csv")
    fetch_and_save(SubCategory, "db_export/sub_category.csv")
    fetch_and_save(ProductBestFor, "db_export/product_best_for.csv")
    fetch_and_save(ProductColor, "db_export/product_colors.csv")
    fetch_and_save(ProductSize, "db_export/product_sizes.csv")
    fetch_and_save(ProductBrand, "db_export/product_brands.csv")
    fetch_and_save(Products, "db_export/products.csv")

    logger.success("All data fetched from the database and saved to CSV files")


def initialize_azzain_db():
    def nan_to_none(value):
        return None if pd.isna(value) else value

    # load banners data
    banners = pd.read_csv("db_export/banners.csv")

    for index, row in banners.iterrows():
        banner = Banner(
            id=nan_to_none(row["id"]),
            name=nan_to_none(row["name"]),
            name_ar=nan_to_none(row["name_ar"]),
            img_url=nan_to_none(row["img_url"]),
            redirect_url=nan_to_none(row["redirect_url"]),
        )
        db.session.add(banner)

    logger.info("Banners data added (not committed)")
    db.session.flush()

    # load body_parts data
    body_parts = pd.read_csv("db_export/body_parts.csv")

    for index, row in body_parts.iterrows():
        body_part = BodyPart(
            id=nan_to_none(row["id"]),
            name=nan_to_none(row["name"]),
            name_ar=nan_to_none(row["name_ar"]),
            img_url=nan_to_none(row["img_url"]),
            gender=nan_to_none(row["gender"]),
        )
        db.session.add(body_part)

    logger.info("Body Parts data added (not committed)")
    db.session.flush()

    # load body_shapes data
    body_shapes = pd.read_csv("db_export/body_shapes.csv")

    for index, row in body_shapes.iterrows():
        body_shape = BodyShape(
            id=nan_to_none(row["id"]),
            name=nan_to_none(row["name"]),
            name_ar=nan_to_none(row["name_ar"]),
            gender=nan_to_none(row["gender"]),
            img_url=nan_to_none(row["img_url"]),
        )
        db.session.add(body_shape)

    logger.info("Body Shapes data added (not committed)")
    db.session.flush()

    # load user_age_group data
    user_age_groups = pd.read_csv("db_export/user_age_group.csv")

    for index, row in user_age_groups.iterrows():
        user_age_group = UserAgeGroup(
            id=nan_to_none(row["id"]),
            name=nan_to_none(row["name"]),
            name_ar=nan_to_none(row["name_ar"]),
        )
        db.session.add(user_age_group)

    logger.info("User Age Groups data added (not committed)")
    db.session.flush()

    # load user_height data
    user_heights = pd.read_csv("db_export/user_height.csv")

    for index, row in user_heights.iterrows():
        user_height = UserHeight(
            id=nan_to_none(row["id"]),
            name=nan_to_none(row["name"]),
            name_ar=nan_to_none(row["name_ar"]),
        )
        db.session.add(user_height)

    logger.info("User Heights data added (not committed)")
    db.session.flush()

    # load user_weight data
    user_weights = pd.read_csv("db_export/user_weight.csv")

    for index, row in user_weights.iterrows():
        user_weight = UserWeight(
            id=nan_to_none(row["id"]),
            name=nan_to_none(row["name"]),
            name_ar=nan_to_none(row["name_ar"]),
        )
        db.session.add(user_weight)

    logger.info("User Weights data added (not committed)")
    db.session.flush()

    # load user_budget data
    user_budgets = pd.read_csv("db_export/user_budget.csv")

    for index, row in user_budgets.iterrows():
        user_budget = UserBudget(
            id=nan_to_none(row["id"]),
            name=nan_to_none(row["name"]),
            name_ar=nan_to_none(row["name_ar"]),
        )
        db.session.add(user_budget)

    logger.info("User Budgets data added (not committed)")
    db.session.flush()

    # load cloth_colors data
    cloth_colors = pd.read_csv("db_export/cloth_colors.csv")
    for index, row in cloth_colors.iterrows():
        cloth_color = ClothColor(
            id=nan_to_none(row["id"]),
            combinations=eval(nan_to_none(row["combinations"])),
            gender=nan_to_none(row["gender"]),
            description=nan_to_none(row["description"]),
        )
        db.session.add(cloth_color)

    logger.info("Cloth Colors data added (not committed)")
    db.session.flush()

    ##############################
    # TODO: load cloth_patterns data
    ##############################

    # load hair_colors data
    hair_color = pd.read_csv("db_export/hair_colors.csv")
    for index, row in hair_color.iterrows():
        hair_color = HairColor(
            id=nan_to_none(row["id"]),
            name=nan_to_none(row["name"]),
            color_code=nan_to_none(row["color_code"]),
        )
        db.session.add(hair_color)

    logger.info("Hair Colors data added (not committed)")
    db.session.flush()

    # load skin_tones data
    skin_tone = pd.read_csv("db_export/skin_tones.csv")
    for index, row in skin_tone.iterrows():
        skin_tone = SkinTone(
            id=nan_to_none(row["id"]),
            name=nan_to_none(row["name"]),
            color_code=nan_to_none(row["color_code"]),
        )
        db.session.add(skin_tone)

    logger.info("Skin Tones data added (not committed)")
    db.session.flush()

    # load categories data
    categories = pd.read_csv("db_export/category.csv")

    for index, row in categories.iterrows():
        category = Category(
            id=nan_to_none(row["id"]),
            name=nan_to_none(row["name"]),
            name_ar=nan_to_none(row["name_ar"]),
            img_url=nan_to_none(row["img_url"]),
        )
        db.session.add(category)

    logger.info("Categories data added (not committed)")
    db.session.flush()

    # load sub_categories data
    sub_categories = pd.read_csv("db_export/sub_category.csv")
    db.session.flush()

    for index, row in sub_categories.iterrows():
        sub_category = SubCategory(
            id=nan_to_none(row["id"]),
            name=nan_to_none(row["name"]),
            name_ar=nan_to_none(row["name_ar"]),
            img_url=nan_to_none(row["img_url"]),
            category_id=nan_to_none(row["category_id"]),
        )
        db.session.add(sub_category)

    logger.info("Sub Categories data added (not committed)")
    db.session.flush()

    # load product_best_for data
    product_best_for = pd.read_csv("db_export/product_best_for.csv")

    for index, row in product_best_for.iterrows():
        product_best_for = ProductBestFor(
            id=nan_to_none(row["id"]),
            name=nan_to_none(row["name"]),
            name_ar=nan_to_none(row["name_ar"]),
        )
        db.session.add(product_best_for)

    # load product_colors data
    products_colors = pd.read_csv("db_export/product_colors.csv")

    for index, row in products_colors.iterrows():
        product_color = ProductColor(
            id=nan_to_none(row["id"]),
            name=nan_to_none(row["name"]),
            name_ar=nan_to_none(row["name_ar"]),
            color_hex=nan_to_none(row["color_hex"]),
        )
        db.session.add(product_color)

    logger.info("Product Colors data added (not committed)")
    db.session.flush()

    # load product_sizes data
    products_sizes = pd.read_csv("db_export/product_sizes.csv")

    for index, row in products_sizes.iterrows():
        product_size = ProductSize(
            id=nan_to_none(row["id"]),
            size=nan_to_none(row["size"]),
        )
        db.session.add(product_size)

    logger.info("Product Sizes data added (not committed)")
    db.session.flush()

    # load product_brands data
    products_brands = pd.read_csv("db_export/product_brands.csv")


    for index, row in products_brands.iterrows():
        product_brand = ProductBrand(
            id=nan_to_none(row["id"]),
            name=nan_to_none(row["name"]),
            name_ar=nan_to_none(row["name_ar"]),
        )
        db.session.add(product_brand)

    logger.info("Product Brands data added (not committed)")
    db.session.flush()

    # load products data
    products = pd.read_csv("db_export/products.csv")

    for index, row in products.iterrows():
        product = Products(
            id=nan_to_none(row["id"]),
            product_id=nan_to_none(row["product_id"]),
            name=nan_to_none(row["name"]),
            name_ar=nan_to_none(row["name_ar"]),
            description=nan_to_none(row["description"]),
            description_ar=nan_to_none(row["description_ar"]),
            price=nan_to_none(row["price"]),
            currency=nan_to_none(row["currency"]),
            link=nan_to_none(row["link"]),
            sizes=eval(nan_to_none(row["sizes"])),
            colors=eval(nan_to_none(row["colors"])),
            image_urls=eval(nan_to_none(row["image_urls"])),
            brand_id=nan_to_none(row["brand_id"]),
            category_id=nan_to_none(row["category_id"]),
            sub_category_id=nan_to_none(row["sub_category_id"]),
            tryon_available=nan_to_none(row["tryon_available"]),
            product_uuid=nan_to_none(row["product_uuid"]),
            good_fit=nan_to_none(row["good_fit"]),
            best_for_id=nan_to_none(row["best_for_id"]),
            bg_remove_url=nan_to_none(row["bg_remove_url"]),
        )
        db.session.add(product)

    logger.info("Products data added (not committed)")
    db.session.flush()

    db.session.commit()

    logger.success("All data added to the database")
