from __future__ import annotations

from pathlib import Path

import pytest

from food_classifier.config import DEFAULT_CHECKPOINT_PATH
from food_classifier.labels import default_class_mapping, load_class_mapping, validate_class_mapping


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_class_mapping_has_42_continuous_classes():
    mapping = {int(index): name for index, name in default_class_mapping().items()}
    validate_class_mapping(mapping)
    assert len(mapping) == 42
    assert sorted(mapping) == list(range(42))


def test_class_mapping_file_is_valid():
    mapping = load_class_mapping(PROJECT_ROOT / "models" / "class_mapping.json")
    assert mapping[0] == "achichuk"
    assert mapping[24] == "plov"
    assert mapping[41] == "tushpara-wo-soup"


def test_build_model_output_dimension_when_torch_available():
    pytest.importorskip("torch")
    pytest.importorskip("torchvision")

    from food_classifier.model import build_model, validate_model_output_dim

    model = build_model(pretrained=False)
    validate_model_output_dim(model, 42)


def test_checkpoint_loads_when_available():
    pytest.importorskip("torch")
    if not DEFAULT_CHECKPOINT_PATH.exists():
        pytest.skip("Production checkpoint is not available yet.")

    from food_classifier.model import load_model

    model, checkpoint = load_model(DEFAULT_CHECKPOINT_PATH, device="cpu")
    assert checkpoint["num_classes"] == 42
    assert not model.training


def test_cuda_inference_path_when_available():
    torch = pytest.importorskip("torch")
    if not torch.cuda.is_available():
        pytest.skip("CUDA is not available.")
    if not DEFAULT_CHECKPOINT_PATH.exists():
        pytest.skip("Production checkpoint is not available yet.")

    from food_classifier.model import load_model

    model, _ = load_model(DEFAULT_CHECKPOINT_PATH, device="cuda")
    assert not model.training
