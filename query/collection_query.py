from models import CollectionItems, CollectionName, Products
from request_parsers.products import CollectionCreateRequest, CollectionCreateResponse
from database import db
from recommendation.product_pair_for_category import get_pair_from_category
from logger import logger
from config import Config
import requests

try:
    __tmp = requests.get(
        f"https://v6.exchangerate-api.com/v6/{Config.EXCHANGE_RATE_API_KEY}/latest/USD"
    ).json()
    USD_TO_SAR_FACTOR = __tmp["conversion_rates"]["SAR"]
except Exception as e:
    logger.error(f"Error in getting exchange rate: {e}")
    logger.warning("Defaulting to 3.75 for USD to SAR conversion")
    USD_TO_SAR_FACTOR = 3.75


class CollectionQuery:
    @staticmethod
    def create_collection(
        collection_data: CollectionCreateRequest,
        user_data: dict,
        is_generic: bool = False,
    ) -> CollectionCreateResponse:

        # Create a new collection
        new_collection = CollectionName(
            name=collection_data.name,
            name_ar=collection_data.name_ar,
            img_url=collection_data.img_url,
            user_id=user_data["id"],
            is_generic=False,
        )
        db.session.add(new_collection)
        db.session.flush()

        # Get the category data
        if is_generic:
            category_data = [
                {
                    "category_name": collection_data.name,
                    "sub_category_name": "formal",
                },
                {
                    "category_name": collection_data.name,
                    "sub_category_name": "informal",
                },
            ]
        else:
            category_data = [
                {
                    "category_name": collection_data.name,
                    "sub_category_name": (
                        "formal" if collection_data.is_formal else "informal"
                    ),
                }
            ]

        # Get the favorite items of the user
        fav_topwear_descriptions = (
            Products.query.with_entities(Products.description)
            .filter(Products.product_uuid.in_(user_data["fav_topwear"]))
            .all()
        )
        fav_bottomwear_descriptions = (
            Products.query.with_entities(Products.description)
            .filter(Products.product_uuid.in_(user_data["fav_bottomwear"]))
            .all()
        )
        fav_footwear_descriptions = (
            Products.query.with_entities(Products.description)
            .filter(Products.product_uuid.in_(user_data["fav_footwear"]))
            .all()
        )

        # Update the user_data with descriptions of favorite items
        user_data["fav_topwear"] = ",".join(
            [i.description for i in fav_topwear_descriptions]
        )
        user_data["fav_bottomwear"] = ",".join(
            [i.description for i in fav_bottomwear_descriptions]
        )
        user_data["fav_footwear"] = ",".join(
            [i.description for i in fav_footwear_descriptions]
        )

        # Get the pair of items for the category
        for cd in category_data:
            collection_item_data, _ = get_pair_from_category(user_data, cd)

            # Add the collection items to the database
            for item in collection_item_data:
                total_price = 0.0
                product_data = Products.query.filter(
                    Products.product_uuid.in_(
                        [item["topwear"], item["bottomwear"], item["footwear"]]
                    )
                ).all()
                for p in product_data:
                    if p.currency != "SAR":
                        total_price += p.price * USD_TO_SAR_FACTOR
                    else:
                        total_price += p.price

                new_collection_item = CollectionItems(
                    collection_id=new_collection.id,
                    topwear_uuid=item["topwear"],
                    bottom_wear_uuid=item["bottomwear"],
                    foot_wear_uuid=item["footwear"],
                    formal= True if cd["sub_category_name"] == "formal" else False,
                    currency="SAR",
                    price=total_price,
                )
                db.session.add(new_collection_item)

        db.session.commit()

        return CollectionCreateResponse(collection_id=new_collection.id)

    @staticmethod
    def create_generic_collection_for_user(user_data: dict) -> bool:
        """
        Creates a generic collection for the user
        """
        # Get all generic collection
        generic_collection = CollectionName.query.filter_by(is_generic=True).all()
        # Create a new collection for each generic collection
        for collection in generic_collection:
            logger.info(f"Created collection for {collection.name}")
            logger.info(user_data)
            # Create a new formal collection
            CollectionQuery.create_collection(
                CollectionCreateRequest(
                    name=collection.name,
                    name_ar=collection.name_ar,
                    img_url=collection.img_url,
                    is_formal=True,
                ),
                dict.copy(user_data),
                is_generic=True,
            )
