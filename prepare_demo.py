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
import re
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
from models.banner import Banner
from models.collection_items import CollectionItems
from helpers.utility import insert_collection_item_in_db
from helpers.arabic_names import arabic_product_name
from helpers.images import flatten_on_white
from helpers.styles import classify_style, STYLES
from helpers.tryon_models import garment_for_category

UA = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
DEMO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "demo")
BRANDS = ("TOM FORD", "VALENTINO")
# Per gender, per STYLE (Casual/Formal/Sporty/Trendy), per category — each
# collection tab gets its own disjoint product pool so the four tabs no longer
# look alike. Sized for 5 boards per tab without repeating a product inside a
# collection: hero = topwear+outwear (4+2 >= 5), other slots need >= 5 each.
STYLE_QUOTA = {"topwear": 4, "outwear": 2,
               "bottomwear": 5, "footwear": 5, "accesories": 5}
CATEGORIES = tuple(STYLE_QUOTA)
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
        .filter(ProductBestFor.name.in_([gender, "unisex"]),
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
    """Pick STYLE_QUOTA products per gender+style+category with alive images.

    A product's style comes from classify_style(name) — each product has
    exactly one style, which keeps the four collection tabs disjoint.
    """
    selected = {"men": {}, "women": {}}
    for gender in ("men", "women"):
        for style in STYLES:
            selected[gender][style] = {}
            for category, need in STYLE_QUOTA.items():
                pool = [p for p in candidates(gender, category)
                        if classify_style(p.name) == style]
                picked = []
                for p in pool:
                    urls = source_urls(p)
                    if not urls:
                        continue
                    already = bool(saved_images(
                        os.path.join(DEMO_DIR, str(p.product_uuid))))
                    if already or url_alive(urls[0]):
                        picked.append(p)
                        print(f"  [{gender}/{style}/{category}] "
                              f"{len(picked)}/{need}  {p.name[:50]}")
                    if len(picked) == need:
                        break
                if len(picked) < need:
                    print(f"  WARNING: only {len(picked)}/{need} "
                          f"for {gender}/{style}/{category}")
                selected[gender][style][category] = picked
    return selected


def merge_by_category(selected, gender):
    """Flatten one gender's style buckets into {category: [products]}."""
    merged = {category: [] for category in CATEGORIES}
    seen = set()
    for style in STYLES:
        for category in CATEGORIES:
            for p in selected[gender].get(style, {}).get(category, []):
                if p.product_uuid not in seen:
                    seen.add(p.product_uuid)
                    merged[category].append(p)
    return merged


def saved_images(directory):
    """Demo images already on disk (ignores .DS_Store and other stray files)."""
    if not os.path.isdir(directory):
        return []
    return sorted(f for f in os.listdir(directory) if f.endswith(".jpg"))


def download_images(product):
    """Download+resize up to IMAGES_PER_PRODUCT images; returns count saved."""
    out_dir = os.path.join(DEMO_DIR, str(product.product_uuid))
    existing = saved_images(out_dir)
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
            img = flatten_on_white(Image.open(BytesIO(r.content)))
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


BANNER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "static", "banner")
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp")


def fill_banners(base_url):
    """Point the home-screen banners at the images in static/banner/.

    One banner row per image file, so dropping another image into the folder
    and re-running adds a slide. Rows left without an image are removed —
    they used to reference the unreachable S3 bucket.
    """
    files = sorted(f for f in os.listdir(BANNER_DIR)
                   if f.lower().endswith(IMAGE_SUFFIXES)) \
        if os.path.isdir(BANNER_DIR) else []
    if not files:
        print("  no images in static/banner, banners left unchanged")
        return

    banners = Banner.query.order_by(Banner.id).all()
    for index, filename in enumerate(files):
        url = f"{base_url}/static/banner/{filename}"
        if index < len(banners):
            banners[index].img_url = url
        else:
            db.session.add(Banner(img_url=url))
    for extra in banners[len(files):]:
        db.session.delete(extra)

    db.session.commit()
    print(f"  {len(files)} banner(s) set, "
          f"{max(0, len(banners) - len(files))} stale row(s) removed")


BRANDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "static", "brands")
CATEGORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "static", "category")


def _asset_slug(name):
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def _point_at_assets(model, directory, url_prefix, label):
    """Set img_url on rows whose name matches a file in `directory`."""
    if not os.path.isdir(directory):
        print(f"  no {directory}, {label} left unchanged")
        return
    files = {os.path.splitext(f)[0].lower(): f
             for f in os.listdir(directory)
             if f.lower().endswith(IMAGE_SUFFIXES)}
    matched = missing = 0
    for row in model.query.all():
        filename = files.get(_asset_slug(row.name))
        if filename:
            row.img_url = f"{url_prefix}/{filename}"
            matched += 1
        else:
            missing += 1
            print(f"    no {label} asset for '{row.name}'")
    db.session.commit()
    print(f"  {matched} {label} image(s) set" +
          (f", {missing} without an asset" if missing else ""))


def fill_brand_and_category_images(base_url):
    """Point brand logos and category icons at locally served files.

    Both used to reference the unreachable azzain-bucket S3 (brands ended up
    NULL entirely), so the home screen rendered blank circles above the names.
    """
    _point_at_assets(ProductBrand, BRANDS_DIR,
                     f"{base_url}/static/brands", "brand")
    _point_at_assets(Category, CATEGORY_DIR,
                     f"{base_url}/static/category", "category")


def sync_tryon_flags():
    """Mark every product the try-on model can actually handle.

    The app hides its try-on button when `tryon_available` is false, so the
    flag has to mean exactly what the API accepts: any product whose category
    maps to an OOTD garment class. Footwear, accessories and "Other" stay
    false — the model cannot put shoes or a bag on a person.
    """
    rows = (db.session.query(Products, Category.name.label("category_name"))
            .outerjoin(Category, Products.category_id == Category.id).all())
    enabled = disabled = 0
    for product, category_name in rows:
        capable = garment_for_category(category_name) is not None
        if bool(product.tryon_available) != capable:
            product.tryon_available = capable
            enabled += capable
            disabled += not capable
    db.session.commit()
    print(f"  try-on enabled on {enabled} product(s), cleared on {disabled}")


def fill_arabic_names():
    """Give every demo product an Arabic name (the boards UI is bilingual)."""
    rows = (
        db.session.query(Products, Category.name.label("category_name"))
        .outerjoin(Category, Products.category_id == Category.id)
        .filter(text("products.image_urls_original IS NOT NULL"))
        .all()
    )
    filled = 0
    for product, category_name in rows:
        if not product.name_ar:
            product.name_ar = arabic_product_name(product.name, category_name)
            filled += 1
    db.session.commit()
    print(f"  {filled} Arabic names filled")


def reseed_collections():
    """Rebuild the 'Made for you' boards from the demo products."""
    created, skipped = insert_collection_item_in_db(demo_only=True)
    print(f"  {created} boards created, {skipped} skipped")


def write_recommendations(selected):
    recos = {"good_fit": {}}
    for gender in ("men", "women"):
        merged = merge_by_category(selected, gender)
        flat = [p for cat in CATEGORIES for p in merged[cat]]
        recos[gender] = {"demographics": [str(p.product_uuid) for p in flat]}
        for p in flat:
            own_cat = next(c for c in CATEGORIES if p in merged[c])
            others = [str(o.product_uuid)
                      for cat in CATEGORIES if cat != own_cat
                      for o in merged[cat][:2]]
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
    ap.add_argument("--redownload", action="store_true",
                    help="delete cached demo images and fetch them again")
    args = ap.parse_args()

    with app.app_context():
        ensure_backup_column()
        if args.restore:
            restore()
            return
        if not args.base_url:
            ap.error("--base-url is required (or use --restore)")
        base_url = args.base_url.rstrip("/")

        if args.redownload:
            removed = 0
            for name in os.listdir(DEMO_DIR) if os.path.isdir(DEMO_DIR) else []:
                d = os.path.join(DEMO_DIR, name)
                if not os.path.isdir(d):
                    continue
                for f in os.listdir(d):
                    os.remove(os.path.join(d, f))
                    removed += 1
            print(f"Removed {removed} cached images; they will be fetched again.")

        print("Selecting demo products (checking image links)...")
        selected = select_products()

        print("Downloading + resizing images...")
        done = set()
        for gender in ("men", "women"):
            for style in STYLES:
                for cat in CATEGORIES:
                    for p in selected[gender][style][cat]:
                        if p.product_uuid in done:
                            continue
                        done.add(p.product_uuid)
                        count = download_images(p)
                        if count == 0:
                            print(f"  WARNING: no images saved for {p.name[:50]}")
                            continue
                        rewrite_urls(p, base_url, count)
        db.session.commit()

        print("Re-seeding collections from demo products...")
        print("Setting home banners...")
        fill_banners(base_url)

        print("Setting brand logos and category icons...")
        fill_brand_and_category_images(base_url)

        print("Syncing try-on flags...")
        sync_tryon_flags()

        print("Filling Arabic names...")
        fill_arabic_names()

        print("Building 'Made for you' boards...")
        reseed_collections()

        path = write_recommendations(selected)
        print(f"Done. {len(done)} demo products, recommendations at {path}")
        print("Set DEMO_MODE=1 in .env and restart the API.")


if __name__ == "__main__":
    main()
