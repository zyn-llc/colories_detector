from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image

from food_classifier.predictor import FoodPredictor


def test_invalid_prediction_input_returns_invalid_status():
    predictor = FoodPredictor(
        model=object(),
        checkpoint={"class_names": ["x"] * 42, "version": "v1.0"},
        device=None,
    )
    result = predictor.predict_bytes(b"bad image")
    assert result.status == "invalid_input"
    assert result.error


def test_prediction_returns_top1_and_top3_when_checkpoint_available():
    pytest.importorskip("torch")
    pytest.importorskip("torchvision")
    pytest.importorskip("albumentations")
    pytest.importorskip("cv2")
    pytest.importorskip("numpy")

    from food_classifier.config import DEFAULT_CHECKPOINT_PATH
    from food_classifier.predictor import load_predictor

    if not DEFAULT_CHECKPOINT_PATH.exists():
        pytest.skip("Production checkpoint is not available yet.")

    buffer = BytesIO()
    Image.new("RGB", (256, 256), color=(100, 100, 100)).save(buffer, format="JPEG")
    predictor = load_predictor(force_reload=True)
    result = predictor.predict_bytes(buffer.getvalue(), top_k=3)
    assert result.status in {"recognized", "unknown"}
    assert result.confidence is not None
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.top_3) == 3
    assert all(0.0 <= item.confidence <= 1.0 for item in result.top_3)
