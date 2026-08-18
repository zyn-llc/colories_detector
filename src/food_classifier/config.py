from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"

_CHECKPOINT_ENV = os.getenv("FOOD_AI_CHECKPOINT", "").strip()
if _CHECKPOINT_ENV:
    _checkpoint_override = Path(_CHECKPOINT_ENV).expanduser()
    if not _checkpoint_override.is_absolute():
        _checkpoint_override = PROJECT_ROOT / _checkpoint_override
    DEFAULT_CHECKPOINT_PATH = _checkpoint_override
else:
    DEFAULT_CHECKPOINT_PATH = MODELS_DIR / "efficientnet_b0_central_asian_food_v1.pth"

DEFAULT_CLASS_MAPPING_PATH = MODELS_DIR / "class_mapping.json"
DEFAULT_MODEL_CONFIG_PATH = MODELS_DIR / "model_config.json"


@dataclass(frozen=True)
class ImageValidationConfig:
    allowed_formats: tuple[str, ...] = ("JPEG", "PNG", "WEBP")
    min_width: int = 100
    min_height: int = 100
    max_file_size_mb: int = 15


@dataclass(frozen=True)
class ModelConfig:
    model_name: str = "efficientnet_b0"
    num_classes: int = 42
    image_size: int = 224
    resize_longest_max_size: int = 256
    normalization_mean: tuple[float, float, float] = (0.485, 0.456, 0.406)
    normalization_std: tuple[float, float, float] = (0.229, 0.224, 0.225)
    version: str = "v1.0"


DEFAULT_MODEL_CONFIG = ModelConfig()
DEFAULT_IMAGE_VALIDATION = ImageValidationConfig()
