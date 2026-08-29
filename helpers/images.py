"""Shared image normalisation used by the demo prep and the try-on adapters."""
from PIL import Image


def flatten_on_white(img):
    """RGB copy of img, compositing any transparency onto white.

    Brand packshots are cut-outs on a transparent background. A plain
    `.convert("RGB")` drops the alpha channel without compositing, so
    transparent pixels keep their underlying RGB — which is black. A dark
    garment then arrives at the model as a black shape on a black field with no
    visible edges, collar or buttons.
    """
    if img.mode in ("RGBA", "LA") or (
            img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        out = Image.new("RGB", rgba.size, (255, 255, 255))
        out.paste(rgba, mask=rgba.split()[-1])
        return out
    return img.convert("RGB")


def pad_to_ratio(img, ratio=3 / 4, fill=(255, 255, 255)):
    """Letterbox img onto a white canvas of the given width/height ratio.

    CatVTON centre-crops the person photo to 3:4, which lops off the top of the
    head on a taller frame. Padding first keeps the whole body in view.
    """
    width, height = img.size
    if abs((width / height) - ratio) < 0.01:
        return img
    if (width / height) > ratio:      # too wide -> grow height
        new_w, new_h = width, int(round(width / ratio))
    else:                             # too tall -> grow width
        new_w, new_h = int(round(height * ratio)), height
    canvas = Image.new("RGB", (new_w, new_h), fill)
    canvas.paste(img, ((new_w - width) // 2, (new_h - height) // 2))
    return canvas
