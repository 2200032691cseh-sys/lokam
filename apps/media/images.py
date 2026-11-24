from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

OUTPUT_BYTES = 2 * 1024 * 1024
VARIANT_WIDTHS = {"small": 480, "large": 1600}


class InvalidImage(ValueError):
    pass


def encode_variants(data):
    try:
        with Image.open(BytesIO(data), formats=["JPEG", "PNG", "WEBP"]) as image:
            _validate_shape(image)
            image.verify()
        with Image.open(BytesIO(data), formats=["JPEG", "PNG", "WEBP"]) as image:
            rotated = ImageOps.exif_transpose(image)
            clean = rotated.convert("RGBA" if "A" in rotated.getbands() else "RGB")
            result = {}
            for variant, width in VARIANT_WIDTHS.items():
                rendition = clean.copy()
                rendition.thumbnail((width, width), Image.Resampling.LANCZOS)
                out = BytesIO()
                rendition.save(out, "WEBP", quality=82, method=2)
                body = out.getvalue()
                if not body or len(body) > OUTPUT_BYTES:
                    raise InvalidImage("An image variant exceeded its size limit.")
                result[variant] = (body, rendition.width, rendition.height)
            return result
    except (
        OSError,
        SyntaxError,
        UnidentifiedImageError,
        Image.DecompressionBombError,
    ) as error:
        raise InvalidImage("Upload a valid JPEG, PNG or WebP image.") from error


def _validate_shape(image):
    width, height = image.size
    if (
        width < 1
        or height < 1
        or width > 6000
        or height > 6000
        or width * height > 24_000_000
        or getattr(image, "n_frames", 1) != 1
    ):
        raise InvalidImage("The image exceeds the supported dimensions or frame count.")
