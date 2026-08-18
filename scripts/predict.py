from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from food_classifier.config import DEFAULT_CHECKPOINT_PATH
from food_classifier.predictor import load_predictor


def format_name(slug: str | None) -> str:
    if not slug:
        return "Unknown"
    return slug.replace("-", " ").title()


def main() -> int:
    parser = argparse.ArgumentParser(description="Predict Central Asian food from an image.")
    parser.add_argument("image", type=Path, help="Path to a JPEG, PNG, or WebP image.")
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=DEFAULT_CHECKPOINT_PATH,
        help="Path to the exported production checkpoint.",
    )
    parser.add_argument("--top-k", type=int, default=3, help="Number of candidates to print.")
    args = parser.parse_args()

    predictor = load_predictor(checkpoint_path=args.checkpoint)
    result = predictor.predict_image(args.image, top_k=args.top_k)

    print("=" * 50)
    print("Central Asian Food Classifier")
    print("=" * 50)
    print()

    if result.status == "invalid_input":
        print("Invalid input:")
        print(result.error)
        print()
        print("=" * 50)
        return 2

    print("Prediction:")
    print(format_name(result.prediction))
    print()
    print("Confidence:")
    print(f"{(result.confidence or 0.0) * 100:.2f}%")
    print()
    print("Top 3:")
    for index, item in enumerate(result.top_3, start=1):
        print(f"{index}. {format_name(item.food):<24} {item.confidence * 100:6.2f}%")
    print()
    print(f"Model:\nEfficientNet-B0 {result.model_version}")
    print()
    print("=" * 50)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
