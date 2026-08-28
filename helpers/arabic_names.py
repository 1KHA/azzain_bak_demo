"""Arabic product names for the 'Made for you' boards.

The app is bilingual and the boards spec requires every product on a board to
have both `name` and `name_ar`. Only FENDI products shipped with Arabic names,
so names for the other brands are composed here from the controlled fashion
vocabulary the catalogue actually uses: a garment noun, the material, and any
cut/pattern attribute.

Phrases are matched longest-first so "JEAN JACKET" wins over "JACKET" and
"SWIM SHORT" over "SHORT".
"""

GARMENTS = [
    ("POCKET SQUARE", "منديل جيب"),
    ("MONEY CLIP WALLET", "محفظة بمشبك نقود"),
    ("CHELSEA BOOT", "حذاء تشيلسي"),
    ("COCKTAIL JACKET", "جاكيت سهرة"),
    ("JEAN JACKET", "جاكيت جينز"),
    ("WESTERN SHIRT", "قميص ويسترن"),
    ("PAJAMA SHIRT", "قميص بيجامة"),
    ("MONK STRAP", "حذاء بحزام"),
    ("CAFE RACER", "جاكيت كافيه ريسر"),
    ("SWIM SHORT", "شورت سباحة"),
    ("PORTFOLIO", "حقيبة مستندات"),
    ("LACE UP", "حذاء برباط"),
    ("V NECK", "تيشيرت برقبة V"),
    ("BLOUSON", "جاكيت بلوزون"),
    ("BOMBER", "جاكيت بومبر"),
    ("WESTERN", "جاكيت ويسترن"),
    ("HENLEY", "تيشيرت هنلي"),
    ("TROUSER", "بنطلون"),
    ("BLAZER", "بليزر"),
    ("LOAFER", "حذاء لوفر"),
    ("SANDAL", "صندل"),
    ("WALLET", "محفظة"),
    ("JACKET", "جاكيت"),
    ("SHIRT", "قميص"),
    ("SKIRT", "تنورة"),
    ("SHORTS", "شورت"),
    ("SHORT", "شورت"),
    ("DENIM", "بنطلون جينز"),
    ("SLIDE", "شبشب"),
    ("BOOT", "حذاء بوت"),
    ("POLO", "قميص بولو"),
    ("TOTE", "حقيبة يد"),
    ("BELT", "حزام"),
    ("TIE", "ربطة عنق"),
    ("CAP", "قبعة"),
]

MATERIALS = [
    ("ALLIGATOR", "جلد تمساح"),
    ("PATENT LEATHER", "جلد لامع"),
    ("CHARMEUSE", "شارميوز"),
    ("VISCOSE", "فيسكوز"),
    ("POPLIN", "بوبلين"),
    ("VELVET", "مخمل"),
    ("LEATHER", "جلد"),
    ("SUEDE", "شامواه"),
    ("CANVAS", "قماش كانفا"),
    ("MIKADO", "ميكادو"),
    ("NAPPA", "جلد نابا"),
    ("CUPRO", "كوبرو"),
    ("NYLON", "نايلون"),
    ("COTTON", "قطن"),
    ("TWILL", "تويل"),
    ("FAILLE", "فاي"),
    ("CROC", "جلد تمساح"),
    ("KNIT", "تريكو"),
    ("SILK", "حرير"),
    ("WOOL", "صوف"),
]

ATTRIBUTES = [
    ("STANDARD FIT", "بقصة عادية"),
    ("LONG SLEEVE", "بأكمام طويلة"),
    ("FLUID FIT", "بقصة انسيابية"),
    ("SLIM FIT", "بقصة ضيقة"),
    ("POLKA DOT", "بنقشة نقاط"),
    ("TAILORED", "مفصل"),
    ("RUFFLED", "بكشكشة"),
    ("LEOPARD", "بنقشة النمر"),
    ("FLORAL", "بنقشة زهور"),
    ("STRIPE", "مخطط"),
    ("PLEAT", "بثنيات"),
    ("SHEER", "شفاف"),
]

# used when the name carries no garment word we know
CATEGORY_FALLBACK = {
    "topwear": "قطعة علوية",
    "bottomwear": "قطعة سفلية",
    "footwear": "حذاء",
    "outwear": "جاكيت",
    "accesories": "إكسسوار",
    "dresses": "فستان",
}


def _first_match(text, table):
    for english, arabic in table:
        if english in text:
            return arabic
    return None


def arabic_product_name(name, category_name=None):
    """Compose an Arabic name like 'قميص حرير بقصة ضيقة' from an English one."""
    text = (name or "").upper()

    garment = _first_match(text, GARMENTS) or CATEGORY_FALLBACK.get(
        (category_name or "").lower(), "قطعة")
    parts = [garment]

    material = _first_match(text, MATERIALS)
    if material and material not in garment:
        parts.append(material)

    attribute = _first_match(text, ATTRIBUTES)
    if attribute:
        parts.append(attribute)

    return " ".join(parts)
