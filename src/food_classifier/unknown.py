"""Unknown / out-of-distribution rejection.

The classifier always produces a probability over its 42 known classes, so a photo of
a laptop still yields a food label. Rejecting those requires a decision rule on top of
the softmax output.

Three signals are used, because they fail in different ways:

  confidence  max softmax probability. Low when the model is unsure overall.
  margin      p(top1) - p(top2). Low when the model is torn between two classes, even
              if p(top1) is high-ish. Catches the shashlyk-style confusions.
  entropy     Shannon entropy normalised to [0, 1] by log(num_classes). High when
              probability is spread thinly across many classes, which is the typical
              signature of an image unlike anything in training.

The thresholds are NOT hardcoded. They are produced by scripts/calibrate_unknown.py
from labelled images and stored in models/unknown_policy.json. Until that file exists,
the policy is inactive and nothing is rejected -- an uncalibrated guess would be worse
than no rejection, because it would silently hide correct predictions.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

from food_classifier.config import MODELS_DIR


UNKNOWN_POLICY_PATH = MODELS_DIR / "unknown_policy.json"


@dataclass(frozen=True)
class UnknownSignals:
    confidence: float
    margin: float
    entropy: float

    def as_dict(self) -> dict:
        return {
            "confidence": round(self.confidence, 6),
            "margin": round(self.margin, 6),
            "entropy": round(self.entropy, 6),
        }


@dataclass(frozen=True)
class UnknownPolicy:
    """Thresholds derived from data. None disables that individual signal."""

    min_confidence: float | None = None
    min_margin: float | None = None
    max_entropy: float | None = None
    calibrated_on: str | None = None
    target_false_unknown_rate: float | None = None

    @property
    def is_active(self) -> bool:
        return any(
            value is not None
            for value in (self.min_confidence, self.min_margin, self.max_entropy)
        )

    def evaluate(self, signals: UnknownSignals) -> tuple[bool, list[str]]:
        """Return (is_unknown, reasons). Any single tripped signal rejects."""
        reasons: list[str] = []

        if self.min_confidence is not None and signals.confidence < self.min_confidence:
            reasons.append(
                f"confidence {signals.confidence:.3f} < {self.min_confidence:.3f}"
            )
        if self.min_margin is not None and signals.margin < self.min_margin:
            reasons.append(f"margin {signals.margin:.3f} < {self.min_margin:.3f}")
        if self.max_entropy is not None and signals.entropy > self.max_entropy:
            reasons.append(f"entropy {signals.entropy:.3f} > {self.max_entropy:.3f}")

        return bool(reasons), reasons

    def to_dict(self) -> dict:
        return {
            "min_confidence": self.min_confidence,
            "min_margin": self.min_margin,
            "max_entropy": self.max_entropy,
            "calibrated_on": self.calibrated_on,
            "target_false_unknown_rate": self.target_false_unknown_rate,
        }

    @classmethod
    def inactive(cls) -> "UnknownPolicy":
        return cls()

    @classmethod
    def load(cls, path: Path | None = None) -> "UnknownPolicy":
        policy_path = Path(path) if path is not None else UNKNOWN_POLICY_PATH
        if not policy_path.exists():
            return cls.inactive()
        raw = json.loads(policy_path.read_text(encoding="utf-8"))
        return cls(
            min_confidence=raw.get("min_confidence"),
            min_margin=raw.get("min_margin"),
            max_entropy=raw.get("max_entropy"),
            calibrated_on=raw.get("calibrated_on"),
            target_false_unknown_rate=raw.get("target_false_unknown_rate"),
        )

    def save(self, path: Path | None = None) -> Path:
        policy_path = Path(path) if path is not None else UNKNOWN_POLICY_PATH
        policy_path.parent.mkdir(parents=True, exist_ok=True)
        policy_path.write_text(
            json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8"
        )
        return policy_path


def compute_signals(probabilities) -> UnknownSignals:
    """Derive the three signals from a 1-D probability sequence."""
    values = sorted((float(value) for value in probabilities), reverse=True)
    if len(values) < 2:
        raise ValueError("Need at least two classes to compute a margin.")

    entropy = -sum(p * math.log(p) for p in values if p > 0.0)
    normalized_entropy = entropy / math.log(len(values))

    return UnknownSignals(
        confidence=values[0],
        margin=values[0] - values[1],
        entropy=normalized_entropy,
    )
