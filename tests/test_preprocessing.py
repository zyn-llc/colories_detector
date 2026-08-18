from __future__ import annotations

import pytest
from PIL import Image


def test_inference_preprocessing_shape():
    pytest.importorskip("torch")
    pytest.importorskip("albumentations")
    pytest.importorskip("cv2")
    pytest.importorskip("numpy")

    from food_classifier.preprocessing import preprocess_pil_image

    image = Image.new("RGB", (320, 240), color=(20, 120, 200))
    tensor = preprocess_pil_image(image)
    assert tuple(tensor.shape) == (1, 3, 224, 224)


def test_training_and_inference_transforms_are_separate():
    pytest.importorskip("albumentations")
    pytest.importorskip("cv2")
    pytest.importorskip("torch")

    from food_classifier.preprocessing import build_inference_transform, build_training_transform

    train_names = [type(transform).__name__ for transform in build_training_transform().transforms]
    inference_names = [type(transform).__name__ for transform in build_inference_transform().transforms]
    assert "RandomCrop" in train_names
    assert "CenterCrop" in inference_names
    assert "RandomCrop" not in inference_names
