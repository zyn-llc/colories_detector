from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image

from food_classifier.validation import ImageValidationError, validate_image_bytes


def image_bytes(fmt: str, size: tuple[int, int] = (128, 128), mode: str = "RGB") -> bytes:
    buffer = BytesIO()
    Image.new(mode, size, color=(128, 64, 32)).save(buffer, format=fmt)
    return buffer.getvalue()


def test_jpeg_png_and_webp_are_accepted():
    for fmt in ("JPEG", "PNG", "WEBP"):
        validated = validate_image_bytes(image_bytes(fmt))
        assert validated.image.mode == "RGB"
        assert validated.width == 128
        assert validated.height == 128


def test_rgb_conversion_works():
    validated = validate_image_bytes(image_bytes("PNG", mode="RGBA"))
    assert validated.image.mode == "RGB"


def test_invalid_image_is_rejected():
    with pytest.raises(ImageValidationError):
        validate_image_bytes(b"not an image")


def test_too_small_image_is_rejected():
    with pytest.raises(ImageValidationError):
        validate_image_bytes(image_bytes("PNG", size=(32, 32)))
