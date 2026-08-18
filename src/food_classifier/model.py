from __future__ import annotations

from pathlib import Path
from typing import Any

from food_classifier.config import DEFAULT_CHECKPOINT_PATH, DEFAULT_MODEL_CONFIG, ModelConfig
from food_classifier.labels import validate_class_mapping


class ModelLoadError(RuntimeError):
    """Raised when the model architecture or checkpoint cannot be loaded safely."""


def _require_torch():
    try:
        import torch
        import torch.nn as nn
        import torchvision.models as models
    except ImportError as exc:
        raise ImportError(
            "torch and torchvision are required for model loading. "
            "Install project requirements first."
        ) from exc
    return torch, nn, models


def build_model(config: ModelConfig = DEFAULT_MODEL_CONFIG, pretrained: bool = False):
    torch, nn, models = _require_torch()
    weights = None
    if pretrained:
        weights = models.EfficientNet_B0_Weights.DEFAULT

    model = models.efficientnet_b0(weights=weights)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, config.num_classes),
    )
    return model


def _classifier_output_dim(model: Any) -> int:
    try:
        return int(model.classifier[1].out_features)
    except Exception as exc:
        raise ModelLoadError("Could not determine classifier output dimension.") from exc


def validate_model_output_dim(model: Any, expected_num_classes: int) -> None:
    actual = _classifier_output_dim(model)
    if actual != expected_num_classes:
        raise ModelLoadError(
            f"Model output dimension mismatch. Expected {expected_num_classes}, got {actual}."
        )


def load_checkpoint(path: str | Path = DEFAULT_CHECKPOINT_PATH, device: str | None = None) -> dict[str, Any]:
    torch, _, _ = _require_torch()
    checkpoint_path = Path(path)
    if not checkpoint_path.exists():
        raise ModelLoadError(
            f"Checkpoint not found: {checkpoint_path}. Export the notebook model first."
        )

    map_location = device or ("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(checkpoint_path, map_location=map_location)
    if not isinstance(checkpoint, dict):
        raise ModelLoadError("Checkpoint must be a dictionary.")
    if "model_state_dict" not in checkpoint:
        raise ModelLoadError("Checkpoint is missing 'model_state_dict'.")
    return checkpoint


def load_model(
    checkpoint_path: str | Path = DEFAULT_CHECKPOINT_PATH,
    device: str | None = None,
):
    torch, _, _ = _require_torch()
    checkpoint = load_checkpoint(checkpoint_path, device=device)

    class_names = checkpoint.get("class_names")
    num_classes = int(checkpoint.get("num_classes", DEFAULT_MODEL_CONFIG.num_classes))
    if class_names is not None:
        mapping = {index: str(name) for index, name in enumerate(class_names)}
        validate_class_mapping(mapping, expected_num_classes=num_classes)

    config = ModelConfig(num_classes=num_classes)
    model = build_model(config=config, pretrained=False)
    validate_model_output_dim(model, num_classes)

    map_location = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(map_location)
    model.eval()
    return model, checkpoint
