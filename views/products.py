from flask_restx import Namespace, Resource
from helpers.error_codes import error_codes
from helpers.auth import login_required
from responses import BaseResponse
from database import db
from models.products import Products
from models.products import ProductListingSchema
from models.products import ProductSchema
from helpers.utility import (
    insert_products_in_db,
    insert_collections_in_db,
    insert_collection_item_in_db,
)
from models.product_brand import ProductBrand
from models.banner import Banner, BannerSchema
from models.product_brand import ProductBrandSchema
from models.product_color import ProductColor
from models.product_color import ProductColorSchema
from models.product_size import ProductSize
from models.product_size import ProductSizeSchema
from models.favorite import FavoriteProduct
from models.category import Category
from models.category import CategorySchema
from models.sub_category import SubCategory
from models.sub_category import SubCategorySchema
from models.user_search import UserSearch
from models.usercart import UserCart
from models.usercart import UserCartSchema
from models.product_best_for import ProductBestFor
from models.visited_products import VisitedProducts, VisitedProductsSchema
from models.collection_name import CollectionName
from models.collection_name import CollectionNameSchema
from models.collection_items import CollectionItems
from models.collection_items import CollectionItemsSchema
from request_parsers.products import LikeProductRequest
from models.user import User
from helpers.auth import login_required
from helpers.recommendation import get_product_detail_by_uuid
from flask import request, g, send_file
from sqlalchemy import any_, case, literal, and_, func
from sqlalchemy.orm import aliased
from logger import logger
import random
from datetime import datetime
from query.product_query import ProductQuery
from query.collection_query import CollectionQuery
import requests
from io import BytesIO
from PIL import Image
import os
import urllib.request
from request_parsers.products import CollectionCreateRequest, CollectionCreateResponse
from recommendation.similar_items import get_similar_items
from recommendation.recent_search import (
    do_recent_search_by_product_ids,
    do_recent_search_by_product_description,
)
from recommendation.user_demographics_and_likes_specific import (
    get_recommendation_by_user_demographics,
)
from recommendation.good_fit_for_this_cloths import (
    get_good_fit_products_for_selected_product,
)
from helpers.recommendation import get_user_data
from celery_tasks.collection.tasks import create_generic_collection_for_user

products_api = Namespace("product", description="Product related operations")


# initialize the products
@products_api.route("/initialize")
class InitializeProducts(Resource):
    def get(self):
        """
        Initialize products in database
        """
        insert_products_in_db()
        return BaseResponse.success("Products initialized successfully")


# Get all the brands
@products_api.route("/brands")
class GetAllBrands(Resource):
    def get(self):
        """
        Get All Brands value
        """
        brand_data = ProductQuery.get_all_brands(db)
        return BaseResponse.success(brand_data)


# Get all the banners
@products_api.route("/banners")
class GetAllBanners(Resource):
    def get(self):
        """
        Get All Banners value
        """
        banner_data = ProductQuery.get_all_banners(db)
        return BaseResponse.success(banner_data)


# get all the sizes
@products_api.route("/sizes")
class GetAllSizes(Resource):
    def get(self):
        """
        Get all Sizes Value
        """
        size_data = ProductQuery.get_all_sizes(db)
        return BaseResponse.success(size_data)


# get the colors
@products_api.route("/colors")
class GetAllColors(Resource):
    def get(self):
        """
        Get all color data
        """
        color_data = ProductQuery.get_all_colors(db)
        return BaseResponse.success(color_data)


# get all the category
@products_api.route("/category")
class GetallCategory(Resource):
    def get(self):
        """
        Get all category data
        """
        Category_data = ProductQuery.get_all_category(db)
        return BaseResponse.success(Category_data)


# get all sub category
@products_api.route("/sub-category")
class GetSubcategory(Resource):
    def get(self):
        """
        Get all Sub Category data
        """
        id = request.args.get("id", None, type=int)
        sub_category = ProductQuery.get_all_sub_category(db, id)
        return BaseResponse.success(sub_category)


# get product by Id
@products_api.route("/<int:id>")
class GetProductById(Resource):
    @login_required
    def get(self, id):
        """
        Get product By ID
        TODO:
        Need to work on category and subcategory table joins
        """
        product_id_data = ProductQuery.get_product_by_id(db, id)
        if product_id_data is None:
            return BaseResponse.bad_request(1022, error_codes[1022])
        product_exist_visited = ProductQuery.add_product_to_visited(db, id)
        db.session.commit()

        product_data = ProductSchema().dump(product_id_data)
        check_product_in_cart = UserCart.query.filter_by(
            user_id=g.user.id, product_id=id
        ).first()
        product_data["is_in_cart"] = "yes" if check_product_in_cart else "no"

        return BaseResponse.success(
            {
                "product_data": product_data,
            }
        )


# Get all products
@products_api.route("/listing")
class GetProductData(Resource):
    @login_required
    def get(self):
        """
        Get Product Data using filters
        TODO:
        Need to work on category and subcategory table joins
        """
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)
        filter_data = request.args.get("filter", None, type=str)
        filter_params = eval(filter_data) if filter_data else {}
        sizes = filter_params.get("size")
        colors = filter_params.get("color")
        # gender = filter.get("gender")
        brands = filter_params.get("brand")
        category = filter_params.get("category")
        subcategory = filter_params.get("subcategory")
        best_for = filter_params.get("best_for")
        sorted_criteria = request.args.get("sort_by", None, type=str)
        sorted_params = eval(sorted_criteria) if sorted_criteria else {}

        products_data, count = ProductQuery.get_all_lisiting_products(
            db,
            sizes,
            colors,
            brands,
            category,
            subcategory,
            best_for,
            sorted_params,
            page,
            limit,
        )

        updated_products = ProductQuery.check_cart(db, products_data)

        if len(products_data) == 0:
            return BaseResponse.not_found(1023, error_codes[1023])
        else:
            return BaseResponse.success(
                {
                    "product_data": updated_products,
                    "page": page,
                    "limit": limit,
                    "count": count,
                }
            )


# like the product
@products_api.route("/like")
class likeProduct(Resource):
    @login_required
    def post(self):
        """
        Like the product
        """
        data = request.get_json()

        try:
            like_product_request = LikeProductRequest(**data)
        except Exception as e:
            logger.error(f"Error in request data: {e}")
            return BaseResponse.bad_request(1027, error_codes[1027])

        existing_liked_products = ProductQuery.like_product(db, like_product_request)
        db.session.commit()
        return BaseResponse.success("Products liked successfully")


# dislike the product
@products_api.route("/dislike")
class DislikeProduct(Resource):
    @login_required
    def post(self):
        """
        dislike the product
        """
        data = request.get_json()

        try:
            dislike_product_request = LikeProductRequest(**data)
        except Exception as e:
            logger.error(f"Error in request data: {e}")
            return BaseResponse.bad_request(1027, error_codes[1027])

        liked_products = ProductQuery.dislike_product(db, dislike_product_request)
        db.session.commit()

        return BaseResponse.success("Products disliked successfully")


# Search the product
@products_api.route("/search")
class ProductSearch(Resource):
    @login_required
    def get(self):
        """
        Search product based on query with pagination

        TODO:
        - Need helper quadrant DB function to search product
        - Currently it is just searching in product description
        - In the case of pagination, the same search query is
        gonna insert in the user_search table. Need to find solution for this.
        """
        query = request.args.get("query", None, type=str)
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        if query is None:
            return BaseResponse.bad_request(1006, error_codes[1006])

        user_search = ProductQuery.add_search_query(db, query)
        db.session.commit()

        (products_data, count) = ProductQuery.filter_product_by_query(
            db, query, page, limit
        )

        if len(products_data) == 0:
            return BaseResponse.not_found(1023, error_codes[1023])

        return BaseResponse.success(
            {
                "product_data": products_data,
                "count": count,
                "page": page,
                "limit": limit,
            },
            "Search query executed successfully",
        )


# Add product to cart
@products_api.route("/cart")
class ProductCart(Resource):
    @login_required
    def post(self):
        """
        Add Product in Cart
        """
        data = request.get_json()
        # check that product Id is valid
        validate_product_Id = ProductQuery.check_product_id_present(db, data)
        if validate_product_Id is None:
            return BaseResponse.bad_request(1025, error_codes[1025])

        # Check that product is already present in cart
        product_in_cart = ProductQuery.check_product_already_in_cart(db, data)
        if product_in_cart:
            return BaseResponse.bad_request(1033, error_codes[1033])

        card_data = ProductQuery.add_product_to_cart(db, data)
        db.session.commit()

        return BaseResponse.created("Product Added to Cart Successfully")

    @login_required
    def delete(self):
        """
        Delete product from cart
        """
        data = request.get_json()

        # check that product Id is valid
        validate_product_Id = ProductQuery.validate_product_id(db, data)
        if validate_product_Id is None:
            return BaseResponse.bad_request(1025, error_codes[1025])

        # Check that product of the Product Id is present in cart
        product_in_cart = ProductQuery.check_product_already_in_cart(db, data)
        if product_in_cart is None:
            return BaseResponse.bad_request(1032, error_codes[1032])

        db.session.delete(product_in_cart)

        db.session.commit()

        return BaseResponse.success("Product deleted successfully")

    @login_required
    def get(self):
        """
        Get product from cart
        """
        data = ProductQuery.get_product_from_cart(db)
        if len(data) == 0:
            return BaseResponse.not_found(1034, error_codes[1034])

        return BaseResponse.success(data)


# get product by category
@products_api.route("/recommend/<string:category_name>")
class GetProductByCategory(Resource):
    @login_required
    def get(self, category_name: str):
        """
        Get product by category
        """
        user = g.user

        gender = request.args.get("gender", None, type=str)

        category_name = category_name.lower()
        if category_name not in ["topwear", "bottomwear", "footwear"]:
            logger.error("Invalid category name provided")
            return BaseResponse.bad_request(1006, error_codes[1006])

        res = ProductQuery.get_product_by_category(db, category_name, gender)

        if len(res) == 0:
            logger.info("No products found")
            return BaseResponse.not_found(1023, error_codes[1023])

        data = ProductListingSchema(many=True).dump(res)

        return BaseResponse.success(data)


@products_api.route("/similar-items/<int:product_id>")
class SimilarItems(Resource):
    @login_required
    def get(self, product_id):

        product = Products.query.filter(Products.id == product_id).first()
        if not product:
            return BaseResponse.not_found(1022, error_codes[1022])

        logger.info(f"Similar Items API called: {product_id}")

        product_uuid = product.product_uuid

        similar_items = get_similar_items(str(product_uuid))

        products = (
            db.session.query(
                Products.id.label("id"),
                Products.product_id.label("product_id"),
                Products.name.label("name"),
                Products.description.label("description"),
                Products.name_ar.label("label"),
                Products.description_ar.label("description_ar"),
                Products.price.label("price"),
                Products.currency.label("currency"),
                Products.link.label("link"),
                # Products.sizes.label('sizes'),
                # Products.colors.label('colors'),
                Products.image_urls.label("image_urls"),
                # Products.gender.label('gender'),
                Products.best_for_id.label("best_for_id"),
                ProductBestFor.name.label("best_for_name"),
                Products.brand_id.label("brand_id"),
                ProductBrand.name.label("brand_name"),
                Products.category_id.label("category_id"),
                Category.name.label("category_name"),
                Products.sub_category_id.label("sub_category_id"),
                SubCategory.name.label("sub_category_name"),
                Products.good_fit.label("good_fit"),
                Products.tryon_available.label("tryon_available"),
                case(
                    (FavoriteProduct.product_id != None, literal(True)),
                    else_=literal(False),
                ).label("user_favourite"),
            )
            .outerjoin(
                FavoriteProduct,
                and_(
                    Products.id == FavoriteProduct.product_id,
                    FavoriteProduct.user_id == g.user.id,
                ),
            )
            .outerjoin(ProductBrand, Products.brand_id == ProductBrand.id)
            .outerjoin(Category, Products.category_id == Category.id)
            .outerjoin(SubCategory, Products.sub_category_id == SubCategory.id)
            .outerjoin(ProductBestFor, Products.best_for_id == ProductBestFor.id)
            .filter(Products.product_uuid.in_(similar_items))
        )

        products_data = ProductListingSchema(many=True).dump(products)

        if len(products_data) == 0:
            return BaseResponse.not_found(1023, error_codes[1023])

        return BaseResponse.success(
            {
                "product_data": products_data,
            },
            "Similar Items returned Successfully!",
        )


@products_api.route("/recent-search")
class RecentSearch(Resource):
    @login_required
    def get(self):

        searches = (
            UserSearch.query.filter(UserSearch.user_id == g.user.id).limit(10).all()
        )

        search_history = [search.search_query for search in searches]

        recent_searches = do_recent_search_by_product_description(search_history)

        # Start query with join
        products = (
            db.session.query(
                Products.id.label("id"),
                Products.product_id.label("product_id"),
                Products.name.label("name"),
                Products.description.label("description"),
                Products.name_ar.label("label"),
                Products.description_ar.label("description_ar"),
                Products.price.label("price"),
                Products.currency.label("currency"),
                Products.link.label("link"),
                # Products.sizes.label('sizes'),
                # Products.colors.label('colors'),
                Products.image_urls.label("image_urls"),
                # Products.gender.label('gender'),
                Products.best_for_id.label("best_for_id"),
                ProductBestFor.name.label("best_for_name"),
                Products.brand_id.label("brand_id"),
                ProductBrand.name.label("brand_name"),
                Products.category_id.label("category_id"),
                Category.name.label("category_name"),
                Products.sub_category_id.label("sub_category_id"),
                SubCategory.name.label("sub_category_name"),
                Products.good_fit.label("good_fit"),
                Products.tryon_available.label("tryon_available"),
                case(
                    (FavoriteProduct.product_id != None, literal(True)),
                    else_=literal(False),
                ).label("user_favourite"),
            )
            .outerjoin(
                FavoriteProduct,
                and_(
                    Products.id == FavoriteProduct.product_id,
                    FavoriteProduct.user_id == g.user.id,
                ),
            )
            .outerjoin(ProductBrand, Products.brand_id == ProductBrand.id)
            .outerjoin(Category, Products.category_id == Category.id)
            .outerjoin(SubCategory, Products.sub_category_id == SubCategory.id)
            .outerjoin(ProductBestFor, Products.best_for_id == ProductBestFor.id)
            .filter(Products.product_uuid.in_(recent_searches))
        )

        products_data = ProductListingSchema(many=True).dump(products)

        if len(products_data) == 0:
            return BaseResponse.not_found(1023, error_codes[1023])
        else:
            return BaseResponse.success({"product_data": products_data})


@products_api.route("/demographics-recommendation")
class DemographicsRecommendation(Resource):
    @login_required
    def get(self):

        user_data = get_user_data(user_id=g.user.id)

        recommended_products = get_recommendation_by_user_demographics(user_data)

        # Start query with join
        products = (
            db.session.query(
                Products.id.label("id"),
                Products.product_id.label("product_id"),
                Products.name.label("name"),
                Products.description.label("description"),
                Products.name_ar.label("label"),
                Products.description_ar.label("description_ar"),
                Products.price.label("price"),
                Products.currency.label("currency"),
                Products.link.label("link"),
                # Products.sizes.label('sizes'),
                # Products.colors.label('colors'),
                Products.image_urls.label("image_urls"),
                # Products.gender.label('gender'),
                Products.best_for_id.label("best_for_id"),
                ProductBestFor.name.label("best_for_name"),
                Products.brand_id.label("brand_id"),
                ProductBrand.name.label("brand_name"),
                Products.category_id.label("category_id"),
                Category.name.label("category_name"),
                Products.sub_category_id.label("sub_category_id"),
                SubCategory.name.label("sub_category_name"),
                Products.good_fit.label("good_fit"),
                Products.tryon_available.label("tryon_available"),
                case(
                    (FavoriteProduct.product_id != None, literal(True)),
                    else_=literal(False),
                ).label("user_favourite"),
            )
            .outerjoin(
                FavoriteProduct,
                and_(
                    Products.id == FavoriteProduct.product_id,
                    FavoriteProduct.user_id == g.user.id,
                ),
            )
            .outerjoin(ProductBrand, Products.brand_id == ProductBrand.id)
            .outerjoin(Category, Products.category_id == Category.id)
            .outerjoin(SubCategory, Products.sub_category_id == SubCategory.id)
            .outerjoin(ProductBestFor, Products.best_for_id == ProductBestFor.id)
            .filter(Products.product_uuid.in_(recommended_products))
        )

        products_data = ProductListingSchema(many=True).dump(products)

        if len(products_data) == 0:
            return BaseResponse.not_found(1023, error_codes[1023])
        else:
            return BaseResponse.success({"product_data": products_data})


@products_api.route("/good-fit/<int:product_id>")
class GoodFit(Resource):
    @login_required
    def get(self, product_id):

        product = Products.query.filter(Products.id == product_id).first()
        if not product:
            return BaseResponse.not_found(1022, error_codes[1022])

        user_data = get_user_data(user_id=g.user.id)
        product_uuid = product.product_uuid

        good_fit_items, cat_list = get_good_fit_products_for_selected_product(
            user_data, str(product_uuid)
        )
        logger.info(f"Good Fit API called: {product_id}")

        products = (
            db.session.query(
                Products.id.label("id"),
                Products.product_id.label("product_id"),
                Products.name.label("name"),
                Products.description.label("description"),
                Products.name_ar.label("label"),
                Products.description_ar.label("description_ar"),
                Products.price.label("price"),
                Products.currency.label("currency"),
                Products.link.label("link"),
                # Products.sizes.label('sizes'),
                # Products.colors.label('colors'),
                Products.image_urls.label("image_urls"),
                # Products.gender.label('gender'),
                Products.best_for_id.label("best_for_id"),
                ProductBestFor.name.label("best_for_name"),
                Products.brand_id.label("brand_id"),
                ProductBrand.name.label("brand_name"),
                Products.category_id.label("category_id"),
                Category.name.label("category_name"),
                Products.sub_category_id.label("sub_category_id"),
                SubCategory.name.label("sub_category_name"),
                Products.good_fit.label("good_fit"),
                Products.tryon_available.label("tryon_available"),
                case(
                    (FavoriteProduct.product_id != None, literal(True)),
                    else_=literal(False),
                ).label("user_favourite"),
            )
            .outerjoin(
                FavoriteProduct,
                and_(
                    Products.id == FavoriteProduct.product_id,
                    FavoriteProduct.user_id == g.user.id,
                ),
            )
            .outerjoin(ProductBrand, Products.brand_id == ProductBrand.id)
            .outerjoin(Category, Products.category_id == Category.id)
            .outerjoin(SubCategory, Products.sub_category_id == SubCategory.id)
            .outerjoin(ProductBestFor, Products.best_for_id == ProductBestFor.id)
            .filter(Products.product_uuid.in_(good_fit_items))
        )

        products_data = ProductListingSchema(many=True).dump(products)

        if len(products_data) == 0:
            return BaseResponse.not_found(1023, error_codes[1023])

        return BaseResponse.success(
            {
                "product_data": products_data,
            },
            "Good Fit Items returned Successfully!",
        )


# Add collection category
@products_api.route("/add-collection-names")
class AddCollectionName(Resource):
    def get(self):
        """
        Add the collection Names in db
        """
        insert_collections_in_db()
        return BaseResponse.success("Collection Names inserted successfully")


# Insert collection items
@products_api.route("/insert-collection-items")
class AddCollectionItems(Resource):
    def get(self):
        """
        Add the collection Items in db
        """
        insert_collection_item_in_db()
        return BaseResponse.success("Collection Items inserted successfully")


# Get all collection category
@products_api.route("/get-collection-names")
class GetCollectionName(Resource):
    @login_required
    def get(self):
        """
        Get Collection Name and Id
        """
        data = ProductQuery.get_collection_name_and_id(db)
        return BaseResponse.success(data)


# get collection item with fiters (category and formal)
@products_api.route("/get-collection-by-category")
class GetCollectionByCategory(Resource):
    @login_required
    def get(self):
        """
        Get all data by Category
        """
        filter_data = request.args.get("category", None, type=int)
        formal_filter = request.args.get("filter", None, type=str)

        if formal_filter is not None and formal_filter.lower() not in [
            "formal",
            "informal",
        ]:
            return BaseResponse.bad_request(
                1044, "Invalid value for formal filter. Must be 'formal' or 'informal'."
            )

        formal_filter_bool = None
        if formal_filter is not None:
            formal_filter_bool = True if formal_filter.lower() == "formal" else False

        data = ProductQuery.get_collection_by_category(
            db, filter_data, formal_filter_bool
        )
        if len(data) == 0:
            return BaseResponse.not_found(1043, error_codes[1043])

        for item in data:
            item["topwear"] = get_product_detail_by_uuid(item["topwear_uuid"])
            item["bottom_wear"] = get_product_detail_by_uuid(item["bottom_wear_uuid"])
            item["foot_wear"] = get_product_detail_by_uuid(item["foot_wear_uuid"])
            item["accessories"] = get_product_detail_by_uuid(item["accessories_uuid"])

        return BaseResponse.success(data)


@products_api.route("/create-collection")
class CreateCollection(Resource):
    @login_required
    def post(self):
        """
        Create a collection
        """

        data = request.get_json()

        try:
            collection_data = CollectionCreateRequest(**data)
        except Exception as e:
            logger.error(f"Error in request data: {e}")
            return BaseResponse.bad_request(1011, error_codes[1011])

        user_data = get_user_data(g.user.id)

        # try:
        result: CollectionCreateResponse = CollectionQuery.create_collection(
            collection_data, user_data
        )
        # except Exception as e:
        #     logger.error(f"Error in creating collection: {e}")
        #     return BaseResponse.internal_server_error("Error in creating collection")

        return BaseResponse.success(result.model_dump())


@products_api.route("/generate-generic-collection")
class GenerateGenericCollection(Resource):
    @login_required
    def post(self):
        """
        Generate a generic collection
        """

        create_generic_collection_for_user.delay(g.user.id)

        return BaseResponse.success("Generic collection is being created")
