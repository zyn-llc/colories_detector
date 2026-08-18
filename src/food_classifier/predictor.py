from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO

from PIL import Image

from food_classifier.config import DEFAULT_CHECKPOINT_PATH, DEFAULT_MODEL_CONFIG, ModelConfig
from food_classifier.model import load_model
from food_classifier.preprocessing import preprocess_pil_image
from food_classifier.schemas import PredictionResult, TopKPrediction
from food_classifier.unknown import UnknownPolicy, compute_signals
from food_classifier.validation import (
    ImageValidationError,
    validate_image_bytes,
    validate_image_file,
    validate_image_path,
)


_PREDICTOR: "FoodPredictor | None" = None


@dataclass
class FoodPredictor:
    model: object
    checkpoint: dict
    device: str | None = None
    config: ModelConfig = DEFAULT_MODEL_CONFIG
    #: Manual override. When set it wins over `policy`; used by tests and experiments.
    unknown_threshold: float | None = None
    #: Data-derived rejection rule. Inactive until scripts/calibrate_unknown.py runs.
    policy: UnknownPolicy = field(default_factory=UnknownPolicy.load)

    @property
    def class_names(self) -> list[str]:
        return list(self.checkpoint.get("class_names", []))

    @property
    def model_version(self) -> str:
        return str(self.checkpoint.get("version", self.config.version))

    def _probabilities(self, image: Image.Image):
        """Run the model and return the full probability vector for one image."""
        import torch

        tensor = preprocess_pil_image(image, config=self.config)
        if self.device is not None:
            tensor = tensor.to(self.device)

        with torch.no_grad():
            logits = self.model(tensor)
            probabilities = torch.softmax(logits, dim=1)

        probability_sum = float(probabilities.sum(dim=1).item())
        if abs(probability_sum - 1.0) > 1e-4:
            raise RuntimeError(f"Probability distribution is invalid: sum={probability_sum}")

        return probabilities

    def predict_top_k(self, image: Image.Image, top_k: int = 3) -> list[TopKPrediction]:
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")
        if not self.class_names:
            raise ValueError("Checkpoint does not contain class_names metadata.")
        if top_k > len(self.class_names):
            raise ValueError("top_k cannot exceed the number of classes.")

        probabilities = self._probabilities(image)
        values, indices = probabilities.topk(top_k, dim=1)
        results: list[TopKPrediction] = []
        for value, index in zip(values[0].cpu().tolist(), indices[0].cpu().tolist()):
            confidence = float(value)
            if not 0.0 <= confidence <= 1.0:
                raise RuntimeError(f"Invalid confidence value: {confidence}")
            results.append(
                TopKPrediction(
                    food=self.class_names[int(index)],
                    class_index=int(index),
                    confidence=confidence,
                )
            )
        return results

    def predict_pil(self, image: Image.Image, top_k: int = 3) -> PredictionResult:
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")
        if not self.class_names:
            raise ValueError("Checkpoint does not contain class_names metadata.")
        if top_k > len(self.class_names):
            raise ValueError("top_k cannot exceed the number of classes.")

        probabilities = self._probabilities(image)
        values, indices = probabilities.topk(top_k, dim=1)

        top_predictions: list[TopKPrediction] = []
        for value, index in zip(values[0].cpu().tolist(), indices[0].cpu().tolist()):
            confidence = float(value)
            if not 0.0 <= confidence <= 1.0:
                raise RuntimeError(f"Invalid confidence value: {confidence}")
            top_predictions.append(
                TopKPrediction(
                    food=self.class_names[int(index)],
                    class_index=int(index),
                    confidence=confidence,
                )
            )

        best = top_predictions[0]
        signals = compute_signals(probabilities[0].cpu().tolist())

        # The calibrated policy is the primary rule. unknown_threshold stays supported
        # as a manual override for experiments and for the existing tests.
        status = "recognized"
        if self.unknown_threshold is not None:
            if best.confidence < self.unknown_threshold:
                status = "unknown"
        elif self.policy.is_active:
            is_unknown, _reasons = self.policy.evaluate(signals)
            if is_unknown:
                status = "unknown"

        return PredictionResult(
            status=status,
            prediction=best.food if status == "recognized" else None,
            confidence=best.confidence,
            top_3=top_predictions[:3],
            model_version=self.model_version,
        )

    def predict_image(self, path: str | Path, top_k: int = 3) -> PredictionResult:
        try:
            validated = validate_image_path(path)
            return self.predict_pil(validated.image, top_k=top_k)
        except ImageValidationError as exc:
            return _invalid_result(str(exc), self.model_version)

    def predict_bytes(self, data: bytes, top_k: int = 3) -> PredictionResult:
        try:
            validated = validate_image_bytes(data)
            return self.predict_pil(validated.image, top_k=top_k)
        except ImageValidationError as exc:
            return _invalid_result(str(exc), self.model_version)

    def predict_file(self, file: BinaryIO, top_k: int = 3) -> PredictionResult:
        try:
            validated = validate_image_file(file)
            return self.predict_pil(validated.image, top_k=top_k)
        except ImageValidationError as exc:
            return _invalid_result(str(exc), self.model_version)


def _invalid_result(error: str, version: str) -> PredictionResult:
    return PredictionResult(
        status="invalid_input",
        prediction=None,
        confidence=None,
        top_3=[],
        model_version=version,
        error=error,
    )


def load_predictor(
    checkpoint_path: str | Path = DEFAULT_CHECKPOINT_PATH,
    device: str | None = None,
    unknown_threshold: float | None = None,
    force_reload: bool = False,
) -> FoodPredictor:
    global _PREDICTOR
    if _PREDICTOR is not None and not force_reload:
        return _PREDICTOR

    model, checkpoint = load_model(checkpoint_path=checkpoint_path, device=device)
    actual_device = device
    if actual_device is None:
        try:
            actual_device = str(next(model.parameters()).device)
        except Exception:
            actual_device = None
    _PREDICTOR = FoodPredictor(
        model=model,
        checkpoint=checkpoint,
        device=actual_device,
        unknown_threshold=unknown_threshold,
    )
    return _PREDICTOR
