"""Try-on model adapters: OOTDiffusion and CatVTON.

Both are Hugging Face Spaces driven through gradio_client, but they differ in
input shape, category vocabulary and output format. `run_tryon()` hides that so
`views/ai.py` only deals with "person image + garment image + category".

Pick the backend with TRYON_BACKEND=ootd|catvton in .env.
"""
import os
import tempfile
from io import BytesIO

import requests
from PIL import Image
from gradio_client import Client, handle_file

from config import Config
from helpers.images import flatten_on_white, pad_to_ratio
from logger import logger

# brand CDNs reject the default python-requests agent
UA = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/108.0.0.0 Safari/537.36"}

OOTD_SPACE = "levihsu/OOTDiffusion"
CATVTON_SPACE = "zhengchong/CatVTON"

# product category name -> each Space's own garment vocabulary
OOTD_GARMENTS = {
    "topwear": "Upper-body",
    "outwear": "Upper-body",
    "bottomwear": "Lower-body",
    "dresses": "Dress",
}
CATVTON_GARMENTS = {
    "topwear": "upper",
    "outwear": "upper",
    "bottomwear": "lower",
    "dresses": "overall",
}


def active_backend():
    return (Config.TRYON_BACKEND or "ootd").strip().lower()


def garment_for_category(category_name, backend=None):
    """Garment class for a category, or None if this model cannot wear it."""
    table = (CATVTON_GARMENTS if (backend or active_backend()) == "catvton"
             else OOTD_GARMENTS)
    return table.get((category_name or "").strip().lower())


def _temp_png(image):
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.close()
    image.save(tmp.name, "PNG")
    return tmp.name


def _load(source):
    """Open a local path or an http(s) URL as a PIL image."""
    if str(source).startswith("http"):
        response = requests.get(source, headers=UA, timeout=30)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    return Image.open(source)


def _prepare_garment(source):
    """Garment as a local PNG on a white background.

    Both Spaces do `Image.open(cloth).convert("RGB")`, which turns the
    transparent background of a brand cut-out black — a dark garment then
    becomes invisible to the model. Compositing onto white first is what the
    models expect and fixes it for both backends.
    """
    return _temp_png(flatten_on_white(_load(source)))


def _prepare_person(source, pad=False):
    """Person photo as a local PNG.

    PNG because CatVTON's Space fails with 'cannot write mode RGBA as JPEG' on
    a JPEG. Optionally letterboxed to 3:4 so its centre-crop does not cut off
    the head.
    """
    image = flatten_on_white(_load(source))
    if pad:
        image = pad_to_ratio(image)
    return _temp_png(image)


def _run_ootd(human, cloth, garment):
    client = Client(OOTD_SPACE, token=Config.HF_TOKEN)
    result = client.predict(
        handle_file(_prepare_person(human)),
        handle_file(_prepare_garment(cloth)),
        garment,
        1,
        Config.OOTD_PARAM_STEPS,
        Config.OOTD_PARAM_GUIDANCE_SCALE,
        Config.OOTD_PARAM_SEED,
        api_name=Config.OOTD_PARAM_API_NAME,
    )
    # OOTD returns a gallery
    return result[0]["image"]


def _blank_layer(reference_path):
    """Empty brush layer matching the person image.

    CatVTON reads `person_image["layers"][0]` as a hand-drawn mask, so the key
    must exist or the Space raises IndexError. A single-colour layer is its
    signal for "no manual mask" — it then masks the body automatically.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.close()
    Image.new("RGBA", Image.open(reference_path).size, (0, 0, 0, 0)).save(
        tmp.name, "PNG")
    return tmp.name


def _run_catvton(human, cloth, garment):
    person = _prepare_person(human, pad=True)
    client = Client(CATVTON_SPACE, token=Config.HF_TOKEN)
    result = client.predict(
        person_image={"background": handle_file(person),
                      "layers": [handle_file(_blank_layer(person))],
                      "composite": handle_file(person)},
        cloth_image=handle_file(_prepare_garment(cloth)),
        cloth_type=garment,
        num_inference_steps=Config.CATVTON_PARAM_STEPS,
        guidance_scale=Config.CATVTON_PARAM_GUIDANCE_SCALE,
        seed=Config.CATVTON_PARAM_SEED,
        show_type="result only",
        api_name="/submit_function",
    )
    # CatVTON returns a single image
    return result if isinstance(result, str) else (result or {}).get("path")


def run_tryon(human, cloth, garment):
    """Generate a try-on image; returns a local path or URL to the result."""
    backend = active_backend()
    logger.info(f"Try-on backend: {backend}")
    if backend == "catvton":
        return _run_catvton(human, cloth, garment)
    return _run_ootd(human, cloth, garment)
