from __future__ import annotations

from PIL import Image

from food_classifier.config import DEFAULT_MODEL_CONFIG, ModelConfig


def _require_albumentations():
    try:
        import albumentations as A
        import cv2
        from albumentations.pytorch import ToTensorV2
    except ImportError as exc:
        raise ImportError(
            "Albumentations, opencv-python, and torch are required for preprocessing. "
            "Install project requirements before running inference."
        ) from exc
    return A, cv2, ToTensorV2


def build_training_transform(config: ModelConfig = DEFAULT_MODEL_CONFIG):
    A, cv2, ToTensorV2 = _require_albumentations()
    return A.Compose(
        [
            A.LongestMaxSize(max_size=config.resize_longest_max_size),
            A.PadIfNeeded(
                min_height=config.resize_longest_max_size,
                min_width=config.resize_longest_max_size,
                border_mode=cv2.BORDER_CONSTANT,
            ),
            A.RandomCrop(config.image_size, config.image_size),
            A.HorizontalFlip(p=0.5),
            A.ShiftScaleRotate(
                shift_limit=0.05,
                scale_limit=0.10,
                rotate_limit=15,
                p=0.5,
            ),
            A.ColorJitter(
                brightness=0.2,
                contrast=0.2,
                saturation=0.2,
                hue=0.05,
                p=0.5,
            ),
            A.Normalize(
                mean=config.normalization_mean,
                std=config.normalization_std,
            ),
            ToTensorV2(),
        ]
    )


def build_inference_transform(config: ModelConfig = DEFAULT_MODEL_CONFIG):
    A, cv2, ToTensorV2 = _require_albumentations()
    return A.Compose(
        [
            A.LongestMaxSize(max_size=config.resize_longest_max_size),
            A.PadIfNeeded(
                min_height=config.resize_longest_max_size,
                min_width=config.resize_longest_max_size,
                border_mode=cv2.BORDER_CONSTANT,
            ),
            A.CenterCrop(config.image_size, config.image_size),
            A.Normalize(
                mean=config.normalization_mean,
                std=config.normalization_std,
            ),
            ToTensorV2(),
        ]
    )


def preprocess_pil_image(image: Image.Image, config: ModelConfig = DEFAULT_MODEL_CONFIG):
    try:
        import numpy as np
    except ImportError as exc:
        raise ImportError("numpy is required for preprocessing.") from exc

    rgb = image.convert("RGB")
    transform = build_inference_transform(config)
    transformed = transform(image=np.array(rgb))["image"]
    return transformed.unsqueeze(0)
