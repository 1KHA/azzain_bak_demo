"""Local file storage for try-on images, served as static files.

Replaces the S3 bucket: uploads and generated results are written under
`static/tryon/` and handed to the app as public `/static/tryon/...` URLs, the
same way the demo product images are served.
"""
import os
import random
from urllib.parse import urlparse

from flask import request

from config import Config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TRYON_HUMAN = "tryon/human"
TRYON_OUTPUT = "tryon/output"


def public_base_url():
    """Origin the app should be reached at, e.g. http://srv1922888.hstgr.cloud."""
    configured = getattr(Config, "PUBLIC_BASE_URL", None)
    if configured:
        return configured.rstrip("/")
    # fall back to the host this request came in on (nginx passes it through)
    return request.url_root.rstrip("/")


def _target(subdir, filename):
    directory = os.path.join(STATIC_DIR, subdir)
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, filename)


def random_name(extension):
    return f"{random.randbytes(16).hex()}.{extension.lstrip('.')}"


def save_upload(file_storage, subdir, filename):
    """Persist an uploaded file unchanged; returns (local_path, public_url)."""
    path = _target(subdir, filename)
    file_storage.save(path)
    return path, f"{public_base_url()}/static/{subdir}/{filename}"


def save_image(image, subdir, filename, fmt="JPEG", quality=90):
    """Persist a PIL image; returns (local_path, public_url)."""
    path = _target(subdir, filename)
    image.save(path, fmt, quality=quality)
    return path, f"{public_base_url()}/static/{subdir}/{filename}"


def local_path_for_url(url):
    """Local file behind one of our own /static/ URLs, or None if external."""
    if not url:
        return None
    path = urlparse(url).path if "://" in url else url
    marker = "/static/"
    if marker not in path:
        return None
    candidate = os.path.join(STATIC_DIR, path.split(marker, 1)[1])
    return candidate if os.path.isfile(candidate) else None


def gradio_source(url):
    """What to hand gradio_client for an image.

    Our own static files are passed as local paths so the Space receives an
    upload and never has to reach back into this server (which matters on a
    laptop or behind a firewall). Anything else is passed through as a URL.
    """
    return local_path_for_url(url) or url
