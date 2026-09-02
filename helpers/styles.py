"""Style classification for the Casual / Formal / Sporty / Trendy collections.

Single source of truth used by the demo product selection (prepare_demo.py)
and the board seeder (helpers/utility.py), so a product lands in the same
style bucket everywhere. Classification is keyword-based on the product name —
the catalogue has no style column — and every product gets exactly one style,
which is what keeps the four tabs disjoint.

Order matters: the first matching style wins, and 'casual' is the fallback
for anything unmatched (jeans, plain shirts, suede jackets...).
"""
import re

STYLE_PATTERNS = [
    ("sporty", re.compile(
        r"SWIM|TOWELLING|TRACK|JOGGER|HOODIE|SNEAKER|T-SHIRT|\bTEE\b|JERSEY"
        r"|TECHNICAL|CAMOUFLAGE|BASEBALL|\bCAP\b|RUNNER", re.I)),
    ("formal", re.compile(
        r"TUXEDO|TAILORED|SUIT|BLAZER|COCKTAIL|PLEAT|DERBY|MONK|LACE UP"
        r"|OXFORD|\bTIE\b|POCKET SQUARE|CUFFLINK|FAILLE|MIKADO|SARTORIAL"
        r"|EVENING|TROUSER", re.I)),
    ("trendy", re.compile(
        r"PRINT|LEOPARD|PSYCHEDELIC|FLORAL|EMBROID|SEQUIN|STUD|VLOGO"
        r"|CRYSTAL|METALLIC|SHEER|ANIMALIER|CHAIN", re.I)),
]

STYLES = ("casual", "formal", "sporty", "trendy")


def classify_style(product_name):
    """One of STYLES for a product name; 'casual' when nothing matches."""
    for style, pattern in STYLE_PATTERNS:
        if pattern.search(product_name or ""):
            return style
    return "casual"


def style_for_collection(collection_name):
    """Map a collection tab name to a style tag, or None if unknown."""
    name = (collection_name or "").strip().lower()
    return name if name in STYLES else None
