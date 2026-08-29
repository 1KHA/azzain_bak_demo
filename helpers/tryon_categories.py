"""Which product categories the try-on model can handle.

Single source of truth shared by the API (`views/ai.py`) and the data sync
(`prepare_demo.py`), so the `tryon_available` flag the app reads can never
disagree with what the endpoint actually accepts.

OOTDiffusion only understands three garment classes. Footwear, accessories and
"Other" cannot be tried on at all — jackets and coats go on as upper body.
"""

OOTD_GARMENTS = {
    "topwear": "Upper-body",
    "outwear": "Upper-body",
    "bottomwear": "Lower-body",
    "dresses": "Dress",
}


def garment_for_category(category_name):
    """OOTD garment class for a category name, or None if unsupported."""
    return OOTD_GARMENTS.get((category_name or "").strip().lower())
