"""Populate the local Qdrant instance with product embeddings.

Creates the `ProductCollection` collection (384-dim cosine, matching the
sentence-transformers/all-MiniLM-L6-v2 model used by the recommendation
code) and upserts one point per product:

- id:      product_uuid
- vector:  embedding of the product name + description
- payload: Product ID / Category / Sub-Category / Gender — the payload
           keys the search filters in recommendation/helper/utils.py use.

Gender comes from the product_best_for table; unisex/child/Other products
are indexed as ['men', 'women'] so they match either gender filter.

Run:  source venv/bin/activate && python init_qdrant.py
"""
from qdrant_client import models

from app import app
from database import db
from models.products import Products
from models.category import Category
from models.sub_category import SubCategory
from models.product_best_for import ProductBestFor
from recommendation.helper.utils import client, enbed_model, COLLECTION_NAME

BATCH_SIZE = 256
VECTOR_SIZE = 384


def gender_payload(best_for_name):
    if best_for_name in ("men", "women"):
        return [best_for_name]
    return ["men", "women"]


def initialize_qdrant():
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE, distance=models.Distance.COSINE),
    )

    rows = (
        db.session.query(
            Products.product_uuid,
            Products.name,
            Products.description,
            Category.name.label("category_name"),
            SubCategory.name.label("sub_category_name"),
            ProductBestFor.name.label("best_for_name"),
        )
        .outerjoin(Category, Products.category_id == Category.id)
        .outerjoin(SubCategory, Products.sub_category_id == SubCategory.id)
        .outerjoin(ProductBestFor, Products.best_for_id == ProductBestFor.id)
        .filter(Products.product_uuid.isnot(None))
        .all()
    )
    print(f"Indexing {len(rows)} products into {COLLECTION_NAME} ...")

    for start in range(0, len(rows), BATCH_SIZE):
        batch = rows[start:start + BATCH_SIZE]
        texts = [" ".join(filter(None, (r.name, r.description))) or "product"
                 for r in batch]
        vectors = enbed_model.encode(texts).tolist()

        points = [
            models.PointStruct(
                id=str(r.product_uuid),
                vector=vec,
                payload={
                    "Product ID": str(r.product_uuid),
                    "Category": r.category_name,
                    "Sub-Category": r.sub_category_name,
                    "Gender": gender_payload(r.best_for_name),
                },
            )
            for r, vec in zip(batch, vectors)
        ]
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"  {min(start + BATCH_SIZE, len(rows))}/{len(rows)}")

    info = client.get_collection(COLLECTION_NAME)
    print(f"Done. Collection has {info.points_count} points.")


if __name__ == "__main__":
    with app.app_context():
        initialize_qdrant()
