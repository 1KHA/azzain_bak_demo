"""Try-on model adapters: OOTDiffusion and CatVTON.

Both are Hugging Face Spaces driven through gradio_client, but they differ in
input shape, category vocabulary and output format. `run_tryon()` hides that so
`views/ai.py` only deals with "person image + garment image + category".

Pick the backend with TRYON_BACKEND=ootd|catvton in .env.
"""
import os
import tempfile

from PIL import Image
from gradio_client import Client, handle_file

from config import Config
from logger import logger

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


def _as_png(path):
    """CatVTON's Space fails with 'cannot write mode RGBA as JPEG' when the
    person image is a JPEG; a PNG of the same picture goes through."""
    if str(path).lower().endswith(".png"):
        return path
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.close()
    Image.open(path).convert("RGB").save(tmp.name, "PNG")
    return tmp.name


def _run_ootd(human, cloth, garment):
    client = Client(OOTD_SPACE, token=Config.HF_TOKEN)
    result = client.predict(
        handle_file(human),
        handle_file(cloth),
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
    person = _as_png(human)
    client = Client(CATVTON_SPACE, token=Config.HF_TOKEN)
    result = client.predict(
        person_image={"background": handle_file(person),
                      "layers": [handle_file(_blank_layer(person))],
                      "composite": handle_file(person)},
        cloth_image=handle_file(cloth),
        cloth_type=garment,
        num_inference_steps=Config.OOTD_PARAM_STEPS,
        guidance_scale=Config.OOTD_PARAM_GUIDANCE_SCALE,
        seed=Config.OOTD_PARAM_SEED,
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
