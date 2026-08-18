from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from PIL import Image, UnidentifiedImageError

from food_classifier.config import DEFAULT_IMAGE_VALIDATION, ImageValidationConfig


class ImageValidationError(ValueError):
    """Raised when an input cannot be used for model inference."""


@dataclass(frozen=True)
class ValidatedImage:
    image: Image.Image
    format: str
    width: int
    height: int


def validate_image_bytes(
    data: bytes,
    config: ImageValidationConfig = DEFAULT_IMAGE_VALIDATION,
) -> ValidatedImage:
    max_bytes = config.max_file_size_mb * 1024 * 1024
    if not data:
        raise ImageValidationError("Empty image data.")
    if len(data) > max_bytes:
        raise ImageValidationError(
            f"Image is too large. Maximum size is {config.max_file_size_mb} MB."
        )

    try:
        with Image.open(BytesIO(data)) as opened:
            image_format = opened.format
            width, height = opened.size
            opened.verify()
    except UnidentifiedImageError as exc:
        raise ImageValidationError("Unsupported or unreadable image file.") from exc
    except Exception as exc:
        raise ImageValidationError("Corrupted or unreadable image file.") from exc

    if image_format not in config.allowed_formats:
        allowed = ", ".join(config.allowed_formats)
        raise ImageValidationError(
            f"Unsupported image format {image_format!r}. Supported formats: {allowed}."
        )
    if width < config.min_width or height < config.min_height:
        raise ImageValidationError(
            f"Image is too small. Minimum size is {config.min_width}x{config.min_height}."
        )

    with Image.open(BytesIO(data)) as image:
        rgb = image.convert("RGB")
        rgb.load()

    return ValidatedImage(image=rgb, format=image_format, width=width, height=height)


def validate_image_path(
    path: str | Path,
    config: ImageValidationConfig = DEFAULT_IMAGE_VALIDATION,
) -> ValidatedImage:
    image_path = Path(path)
    if not image_path.exists():
        raise ImageValidationError(f"Image file does not exist: {image_path}")
    if not image_path.is_file():
        raise ImageValidationError(f"Image path is not a file: {image_path}")
    return validate_image_bytes(image_path.read_bytes(), config=config)


def validate_image_file(
    file: BinaryIO,
    config: ImageValidationConfig = DEFAULT_IMAGE_VALIDATION,
) -> ValidatedImage:
    data = file.read()
    return validate_image_bytes(data, config=config)
