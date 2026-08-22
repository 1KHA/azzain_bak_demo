"""Prepare DEMO_MODE data (see mdfiles/DEMO_MODE.md).

- Selects 20 men + 20 women products from brands with verified-alive CDNs
  (TOM FORD / VALENTINO), spread across categories, checking each product's
  first image really returns HTTP 200 before accepting it.
- Downloads up to 3 images per product, resizes to max 600px JPEG q80,
  stores them under static/demo/<product_uuid>/<n>.jpg.
- Backs up the original links into products.image_urls_original (column is
  created if missing) and rewrites products.image_urls to <base-url> links.
- Re-seeds collection_items deterministically from demo products only.
- Writes demo_recommendations.json with fixed outfits per gender.

Run:  source venv/bin/activate && python prepare_demo.py --base-url https://your-api-host
Re-running with a new --base-url only rewrites the URLs (images are cached).
Restore live CDN links with:  python prepare_demo.py --restore
"""
import argparse
import json
import os
import time
from io import BytesIO

import requests
from PIL import Image
from sqlalchemy import text

from app import app
from database import db
from models.products import Products
from models.category import Category
from models.product_best_for import ProductBestFor
from models.product_brand import ProductBrand
from models.collection_name import CollectionName
from models.collection_items import CollectionItems

UA = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
DEMO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "demo")
BRANDS = ("TOM FORD", "VALENTINO")
QUOTA = {"topwear": 6, "bottomwear": 5, "footwear": 4, "outwear": 3, "accesories": 2}
IMAGES_PER_PRODUCT = 3
MAX_SIDE = 600


def ensure_backup_column():
    db.session.execute(text(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS image_urls_original varchar[]"))
    db.session.commit()


THROTTLE_S = 0.8  # pause between CDN requests to avoid rate-limiting


def fetch(url, timeout=15):
    """GET with throttle and one retry after a cool-down on connection errors."""
    for attempt in (1, 2):
        time.sleep(THROTTLE_S)
        try:
            return requests.get(url, headers=UA, timeout=timeout)
        except requests.RequestException:
            if attempt == 1:
                time.sleep(10)
            else:
                raise


def url_alive(url):
    try:
        return fetch(url).status_code == 200
    except requests.RequestException:
        return False


def candidates(gender, category):
    return (
        db.session.query(Products)
        .join(ProductBestFor, Products.best_for_id == ProductBestFor.id)
        .join(Category, Products.category_id == Category.id)
        .join(ProductBrand, Products.brand_id == ProductBrand.id)
        .filter(ProductBestFor.name == gender,
                Category.name == category,
                ProductBrand.name.in_(BRANDS),
                Products.image_urls.isnot(None))
        .order_by(Products.id.asc())
        .all()
    )


def source_urls(product):
    row = db.session.execute(
        text("SELECT image_urls_original FROM products WHERE id=:i"),
        {"i": product.id}).fetchone()
    return row[0] or product.image_urls or []


def select_products():
    """Pick QUOTA products per gender+category whose first image is alive."""
    selected = {"men": {}, "women": {}}
    for gender in ("men", "women"):
        for category, need in QUOTA.items():
            picked = []
            for p in candidates(gender, category):
                urls = source_urls(p)
                if not urls:
                    continue
                p_dir = os.path.join(DEMO_DIR, str(p.product_uuid))
                already = os.path.isdir(p_dir) and len(os.listdir(p_dir)) > 0
                if already or url_alive(urls[0]):
                    picked.append(p)
                    print(f"  [{gender}/{category}] {len(picked)}/{need}  {p.name[:50]}")
                if len(picked) == need:
                    break
            if len(picked) < need:
                print(f"  WARNING: only {len(picked)}/{need} for {gender}/{category}")
            selected[gender][category] = picked
    return selected


def download_images(product):
    """Download+resize up to IMAGES_PER_PRODUCT images; returns count saved."""
    out_dir = os.path.join(DEMO_DIR, str(product.product_uuid))
    existing = sorted(f for f in os.listdir(out_dir)) if os.path.isdir(out_dir) else []
    if existing:
        return len(existing)
    os.makedirs(out_dir, exist_ok=True)
    saved = 0
    for url in source_urls(product):
        if saved == IMAGES_PER_PRODUCT:
            break
        try:
            r = fetch(url)
            r.raise_for_status()
            img = Image.open(BytesIO(r.content))
            img = img.convert("RGB")
            img.thumbnail((MAX_SIDE, MAX_SIDE))
            saved += 1
            img.save(os.path.join(out_dir, f"{saved}.jpg"), "JPEG", quality=80)
        except Exception as e:
            print(f"    skip image ({type(e).__name__}): {url[:80]}")
    return saved


def rewrite_urls(product, base_url, count):
    db.session.execute(text(
        "UPDATE products SET image_urls_original = COALESCE(image_urls_original, image_urls) "
        "WHERE id=:i"), {"i": product.id})
    product.image_urls = [
        f"{base_url}/static/demo/{product.product_uuid}/{n}.jpg"
        for n in range(1, count + 1)]


def reseed_collections(selected):
    """Deterministic outfits: 3 per gender per collection, demo products only."""
    CollectionItems.query.delete()
    collections = CollectionName.query.order_by(CollectionName.id).all()
    for ci, coll in enumerate(collections):
        for gender in ("men", "women"):
            g = selected[gender]
            tops, bottoms, feet, accs = (g["topwear"], g["bottomwear"],
                                         g["footwear"], g["accesories"])
            for oi in range(3):
                k = ci * 3 + oi
                top = tops[k % len(tops)]
                bottom = bottoms[k % len(bottoms)]
                foot = feet[k % len(feet)]
                acc = accs[k % len(accs)]
                db.session.add(CollectionItems(
                    collection_id=coll.id,
                    topwear_uuid=top.product_uuid,
                    bottom_wear_uuid=bottom.product_uuid,
                    foot_wear_uuid=foot.product_uuid,
                    accessories_uuid=acc.product_uuid,
                    price=int(sum(p.price or 0 for p in (top, bottom, foot, acc))),
                    currency="SAR",
                    formal=(coll.name == "Formal"),
                ))
    db.session.commit()


def write_recommendations(selected):
    recos = {"good_fit": {}}
    for gender in ("men", "women"):
        flat = [p for cat in QUOTA for p in selected[gender][cat]]
        recos[gender] = {"demographics": [str(p.product_uuid) for p in flat]}
        for p in flat:
            others = [str(o.product_uuid)
                      for cat in QUOTA if cat != next(
                          c for c in QUOTA if p in selected[gender][c])
                      for o in selected[gender][cat][:2]]
            recos["good_fit"][str(p.product_uuid)] = others[:6]
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "demo_recommendations.json")
    with open(path, "w") as f:
        json.dump(recos, f, indent=2)
    return path


def restore():
    n = db.session.execute(text(
        "UPDATE products SET image_urls = image_urls_original "
        "WHERE image_urls_original IS NOT NULL")).rowcount
    db.session.commit()
    print(f"Restored original image_urls on {n} products.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", help="public base URL of the API, e.g. https://api.example.com")
    ap.add_argument("--restore", action="store_true",
                    help="restore original CDN image_urls and exit")
    args = ap.parse_args()

    with app.app_context():
        ensure_backup_column()
        if args.restore:
            restore()
            return
        if not args.base_url:
            ap.error("--base-url is required (or use --restore)")
        base_url = args.base_url.rstrip("/")

        print("Selecting demo products (checking image links)...")
        selected = select_products()

        print("Downloading + resizing images...")
        for gender in ("men", "women"):
            for cat in QUOTA:
                for p in selected[gender][cat]:
                    count = download_images(p)
                    if count == 0:
                        print(f"  WARNING: no images saved for {p.name[:50]}")
                        continue
                    rewrite_urls(p, base_url, count)
        db.session.commit()

        print("Re-seeding collections from demo products...")
        reseed_collections(selected)

        path = write_recommendations(selected)
        total = sum(len(selected[g][c]) for g in selected for c in selected[g])
        print(f"Done. {total} demo products, recommendations at {path}")
        print("Set DEMO_MODE=1 in .env and restart the API.")


if __name__ == "__main__":
    main()
