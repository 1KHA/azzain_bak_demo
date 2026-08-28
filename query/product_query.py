from database import db
from flask import g
from models.product_brand import ProductBrand, ProductBrandSchema
from models.banner import Banner, BannerSchema
from models.product_size import ProductSize, ProductSizeSchema
from models.product_color import ProductColor, ProductColorSchema
from models.category import Category, CategorySchema
from models.sub_category import SubCategory, SubCategorySchema
from models.products import Products, ProductListingSchema, ProductSchema
from models.product_best_for import ProductBestFor, ProductBestForSchema
from models.favorite import FavoriteProduct
from models.visited_products import VisitedProducts, VisitedProductsSchema
from models.user_search import UserSearch
from models.usercart import UserCart, UserCartSchema
from models.collection_name import CollectionName, CollectionNameSchema
from models.collection_items import CollectionItems, CollectionItemsSchema
from models.user_preference import UserPreference
from models.cloth_color import ClothColor
from models.user_budget import UserBudget
from sqlalchemy import case, literal, and_, or_, func
from responses import BaseResponse
from helpers.error_codes import error_codes
from datetime import datetime
from hashlib import md5

# users.gender (GenderEnum) -> collection_items.gender
GENDER_TO_BOARD = {"Male": "men", "Female": "women"}

# Budget bands are per garment; a board holds four, so the cap is x4.
# Used only to order boards, never to hide them.
BUDGET_CAPS = {
    "Less than 100 riyals": 400,
    "From 100 to 300 riyals": 1200,
    "From 300 to 500 riyals": 2000,
    "More than 500 riyals": None,
}


class ProductQuery:

    @staticmethod
    def get_all_brands(db):
        product_brand_data = ProductBrand.query.all()
        brand_data = ProductBrandSchema(many=True).dump(product_brand_data)
        return brand_data

    @staticmethod
    def get_all_banners(db):
        banners = Banner.query.all()
        banner_data = BannerSchema(many=True).dump(banners)
        return banner_data

    @staticmethod
    def get_all_sizes(db):
        product_size_data = ProductSize.query.all()
        size_data = ProductSizeSchema(many=True).dump(product_size_data)
        return size_data

    @staticmethod
    def get_all_colors(db):
        product_color_data = ProductColor.query.all()
        color_data = ProductColorSchema(many=True).dump(product_color_data)
        return color_data

    @staticmethod
    def get_all_category(db):
        product_category_data = Category.query.all()
        Category_data = CategorySchema(many=True).dump(product_category_data)
        return Category_data

    @staticmethod
    def get_all_sub_category(db, id):
        query = SubCategory.query
        if id is not None:
            query = query.filter_by(category_id=id)
        product_sub_category = query.all()
        sub_category = SubCategorySchema(many=True).dump(product_sub_category)
        return sub_category

    @staticmethod
    def get_all_lisiting_products(
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
    ):
        color_subquery = (
            db.session.query(
                Products.id,
                func.json_object_agg(ProductColor.id, ProductColor.name).label(
                    "colors_updated"
                ),
            )
            .join(ProductColor, ProductColor.id == func.any(Products.colors))
            .group_by(Products.id)
            .subquery()
        )

        size_subquery = (
            db.session.query(
                Products.id,
                func.json_object_agg(ProductSize.id, ProductSize.size).label(
                    "sizes_updated"
                ),
            )
            .join(ProductSize, ProductSize.id == func.any(Products.sizes))
            .group_by(Products.id)
            .subquery()
        )

        query = (
            db.session.query(
                Products.id.label("id"),
                Products.product_id.label("product_id"),
                Products.name.label("name"),
                Products.description.label("description"),
                Products.name_ar.label("name_ar"),
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
                color_subquery.c.colors_updated.label("colors"),
                size_subquery.c.sizes_updated.label("sizes"),
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
            .outerjoin(color_subquery, Products.id == color_subquery.c.id)
            .outerjoin(size_subquery, Products.id == size_subquery.c.id)
        )

        if sizes:
            query = query.filter(Products.sizes.op("&&")(sizes))

        if colors:
            query = query.filter(Products.colors.op("&&")(colors))

        if brands:
            query = query.filter(Products.brand_id.in_(brands))

        if category:
            query = query.filter(Products.category_id.in_(category))

        if subcategory:
            query = query.filter(Products.sub_category_id.in_(subcategory))

        if best_for:
            query = query.filter(Products.best_for_id.in_(best_for))

        fields = sorted_params.keys()
        for field in fields:
            if field not in ["price", "created_at"]:
                return BaseResponse.bad_request(1024, error_codes[1024])
            order = sorted_params.get(field)
            if order == "asc":
                query = query.order_by(getattr(Products, field).asc())
            elif order == "desc":
                query = query.order_by(getattr(Products, field).desc())

        # Count the total number of results before pagination
        count = query.count()

        # Paginate the results
        products = query.paginate(page=page, per_page=limit, error_out=False)

        products_data = ProductListingSchema(many=True).dump(products)

        return (products_data, count)

    @staticmethod
    def check_cart(db, products_data):
        for product in products_data:
            check_product_in_cart = UserCart.query.filter_by(
                user_id=g.user.id, product_id=product["id"]
            ).first()
            product["is_in_cart"] = "yes" if check_product_in_cart else "no"
        return products_data

    @staticmethod
    def get_product_by_id(db, id):
        color_subquery = (
            db.session.query(
                Products.id,
                func.json_object_agg(ProductColor.id, ProductColor.name).label(
                    "colors_updated"
                ),
            )
            .join(ProductColor, ProductColor.id == func.any(Products.colors))
            .group_by(Products.id)
            .subquery()
        )

        size_subquery = (
            db.session.query(
                Products.id,
                func.json_object_agg(ProductSize.id, ProductSize.size).label(
                    "sizes_updated"
                ),
            )
            .join(ProductSize, ProductSize.id == func.any(Products.sizes))
            .group_by(Products.id)
            .subquery()
        )

        product_id_data = None

        product_id_data = (
            Products.query.with_entities(
                Products.id.label("id"),
                Products.product_id.label("product_id"),
                Products.name.label("name"),
                Products.description.label("description"),
                Products.name_ar.label("name_ar"),
                Products.description_ar.label("description_ar"),
                Products.price.label("price"),
                Products.currency.label("currency"),
                Products.link.label("link"),
                Products.sizes.label("sizes"),
                Products.view_count.label("view_count"),
                Products.best_for_id.label("best_for_id"),
                ProductBestFor.name.label("best_for_name"),
                # Products.colors.label('colors'),
                Products.image_urls.label("image_urls"),
                # Products.gender.label('gender'),
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
                color_subquery.c.colors_updated.label("colors"),
                size_subquery.c.sizes_updated.label("sizes"),
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
            .outerjoin(
                color_subquery,
                Products.id == color_subquery.c.id,  # Joining the subquery here
            )
            .outerjoin(size_subquery, Products.id == size_subquery.c.id)
            .filter(Products.id == id)
            .first()
        )

        return product_id_data

    @staticmethod
    def add_product_to_visited(db, id):
        prod_temp = Products.query.filter_by(id=id).first()
        prod_temp.view_count += 1

        visited_product = VisitedProducts.query.filter(
            VisitedProducts.user_id == g.user.id,
        )
        product_exist_visited = visited_product.filter(
            VisitedProducts.product_id == id
        ).first()

        if product_exist_visited:
            # agar pahle se product exist karta hai to uska updated_at update karna hai
            product_exist_visited.updated_at = datetime.utcnow()
        else:
            # agar pahle se product exist nahi karta hai to uska count check karna hai
            visited_count = visited_product.count()
            if visited_count >= 10:
                # agar count 10 se jyada ho gaya hai to sabse purana wala delete karna hai
                least_recently_visited = visited_product.order_by(
                    VisitedProducts.updated_at.asc()
                ).first()
                db.session.delete(least_recently_visited)
            new_visited_product = VisitedProducts(user_id=g.user.id, product_id=id)
            db.session.add(new_visited_product)

        return product_exist_visited

    @staticmethod
    def like_product(db, like_product_request):
        existing_liked_products = (
            FavoriteProduct.query.with_entities(FavoriteProduct.product_id)
            .filter(FavoriteProduct.product_id.in_(like_product_request.product_ids))
            .all()
        )
        existing_liked_products = [
            product.product_id for product in existing_liked_products
        ]
        # Add those products which are not already liked
        for product_id in like_product_request.product_ids:
            if product_id not in existing_liked_products:
                new_liked_product = FavoriteProduct(
                    user_id=g.user.id, product_id=product_id
                )
                db.session.add(new_liked_product)
        return

    @staticmethod
    def dislike_product(db, dislike_product_request):
        liked_products = FavoriteProduct.query.filter(
            FavoriteProduct.product_id.in_(dislike_product_request.product_ids)
        ).all()
        for liked_product in liked_products:
            db.session.delete(liked_product)
        return

    @staticmethod
    def add_search_query(db, query):
        user_search = UserSearch(user_id=g.user.id, search_query=query)
        db.session.add(user_search)
        return

    @staticmethod
    def filter_product_by_query(db, query, page, limit):
        products = Products.query.filter(Products.description.ilike(f"%{query}%"))
        count = products.count()
        products = products.paginate(page=page, per_page=limit, error_out=False)

        products_data = ProductListingSchema(many=True).dump(products)
        return products_data, count

    @staticmethod
    def check_product_id_present(db, data):
        validate_product_id = Products.query.filter_by(id=data["product_id"]).first()
        return validate_product_id

    @staticmethod
    def check_product_already_in_cart(db, data):
        product_in_cart = UserCart.query.filter_by(
            user_id=g.user.id, product_id=data["product_id"]
        ).first()
        return product_in_cart

    @staticmethod
    def add_product_to_cart(db, data):
        card_data = UserCart(user_id=g.user.id, product_id=data["product_id"])
        db.session.add(card_data)
        return card_data

    @staticmethod
    def get_product_from_cart(db):
        cart_data = (
            UserCart.query.with_entities(
                UserCart.id.label("id"),
                UserCart.product_id.label("product_id"),
                UserCart.user_id.label("user_id"),
                Products.name.label("product_name"),
                Products.description.label("product_description"),
                Products.name_ar.label("product_name_ar"),
                Products.description_ar.label("product_description_ar"),
                Products.price.label("price"),
                Products.currency.label("currency"),
                Products.link.label("link"),
                Products.sizes.label("sizes"),
                Products.colors.label("colors"),
                Products.image_urls.label("image_url"),
                Products.best_for_id.label("gender"),
                Products.brand_id.label("brand_id"),
                Products.category_id.label("category_id"),
                Products.sub_category_id.label("sub_category_id"),
                Products.tryon_available.label("tryon_available"),
            )
            .filter(UserCart.user_id == g.user.id)
            .join(Products, UserCart.product_id == Products.id)
            .all()
        )

        data = UserCartSchema(many=True).dump(cart_data)
        return data

    @staticmethod
    def get_product_by_category(db, category_name, gender):
        color_subquery = (
            db.session.query(
                Products.id,
                func.json_object_agg(ProductColor.id, ProductColor.name).label(
                    "colors_updated"
                ),
            )
            .join(ProductColor, ProductColor.id == func.any(Products.colors))
            .group_by(Products.id)
            .subquery()
        )

        size_subquery = (
            db.session.query(
                Products.id,
                func.json_object_agg(ProductSize.id, ProductSize.size).label(
                    "sizes_updated"
                ),
            )
            .join(ProductSize, ProductSize.id == func.any(Products.sizes))
            .group_by(Products.id)
            .subquery()
        )

        query = (
            db.session.query(
                Products.id.label("id"),
                Products.product_id.label("product_id"),
                Products.name.label("name"),
                Products.description.label("description"),
                Products.name_ar.label("name_ar"),
                Products.description_ar.label("description_ar"),
                Products.price.label("price"),
                Products.currency.label("currency"),
                Products.link.label("link"),
                Products.image_urls.label("image_urls"),
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
                color_subquery.c.colors_updated.label("colors"),
                size_subquery.c.sizes_updated.label("sizes"),
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
            .outerjoin(
                color_subquery,
                Products.id == color_subquery.c.id,  # Joining the subquery here
            )
            .outerjoin(size_subquery, Products.id == size_subquery.c.id)
        )
        res = (
            query.filter(Category.name == category_name, ProductBestFor.name == gender)
            .order_by(Products.id.asc())
            .limit(10)
            .all()
        )
        return res

    @staticmethod
    def get_collection_name_and_id(db):
        collection_data = CollectionName.query.filter(
            or_(CollectionName.is_generic.is_(False),
                CollectionName.is_generic.is_(None))
        ).all()
        data = CollectionNameSchema(many=True).dump(collection_data)
        return data

    @staticmethod
    def get_collection_by_category(db, filter_data, formal_filter):
        """Outfit boards for one collection, personalised for the caller.

        Boards of the wrong gender are filtered out; the rest are ordered so
        the ones matching the user's colour palette and budget come first,
        with a per-user tie-break so two users never get the same lookbook
        in the same order.
        """
        query = CollectionItems.query
        if filter_data is not None:
            query = query.filter_by(collection_id=filter_data)
        if formal_filter is not None:
            query = query.filter_by(formal=formal_filter)

        user = getattr(g, "user", None)
        board_gender = GENDER_TO_BOARD.get(
            user.gender.value if user is not None and user.gender else None)
        if board_gender:
            query = query.filter(
                CollectionItems.gender.in_([board_gender, "unisex"]))

        collection_data = query.all()
        collection_data = ProductQuery.rank_boards_for_user(collection_data, user)
        data = CollectionItemsSchema(many=True).dump(collection_data)
        return data

    @staticmethod
    def preferred_color_ids(user):
        """Product colours implied by the user's chosen clothing palettes.

        A palette is stored as hex values plus a description such as
        "Cal Poly Pomona Green, Medium Aquamarine, Teal Deer"; a product colour
        counts as preferred when its name appears in that text.
        """
        if user is None:
            return set()
        preference = (UserPreference.query
                      .filter_by(user_id=user.id)
                      .order_by(UserPreference.id.desc()).first())
        if preference is None or not preference.cloth_color_id:
            return set()

        palettes = ClothColor.query.filter(
            ClothColor.id.in_(preference.cloth_color_id)).all()
        wanted = " ".join((p.description or "").lower() for p in palettes)
        if not wanted:
            return set()
        return {c.id for c in ProductColor.query.all()
                if c.name and c.name.lower() in wanted}

    @staticmethod
    def rank_boards_for_user(boards, user):
        if not boards:
            return boards

        colors = ProductQuery.preferred_color_ids(user)
        budget_cap = None
        if user is not None and user.user_budget_id:
            budget = UserBudget.query.get(user.user_budget_id)
            budget_cap = BUDGET_CAPS.get(getattr(budget, "name", None))

        uuids = {u for b in boards for u in (
            b.topwear_uuid, b.bottom_wear_uuid,
            b.foot_wear_uuid, b.accessories_uuid) if u}
        garments = {
            p.product_uuid: p for p in Products.query.filter(
                Products.product_uuid.in_(uuids)).all()} if uuids else {}

        seed = user.id if user is not None else 0

        def score(board):
            picks = [garments.get(u) for u in (
                board.topwear_uuid, board.bottom_wear_uuid,
                board.foot_wear_uuid, board.accessories_uuid)]
            color_hits = sum(
                1 for p in picks
                if p is not None and colors.intersection(p.colors or []))
            in_budget = (budget_cap is not None
                         and (board.price or 0) <= budget_cap)
            # stable per-user shuffle so the lookbook feels individual
            jitter = md5(f"{seed}:{board.id}".encode()).hexdigest()
            return (-color_hits, 0 if in_budget else 1, jitter)

        return sorted(boards, key=score)
