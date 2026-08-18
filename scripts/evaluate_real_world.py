from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from food_classifier.predictor import load_predictor


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def model_to_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def iter_images(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            yield path


def infer_group(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    if "known" in parts:
        return "known"
    if "unknown" in parts:
        return "unknown"
    if "non_food" in parts:
        return "non_food"
    return "unlabeled"


def infer_ground_truth(input_root: Path, image_path: Path, group: str) -> str | None:
    if group != "known":
        return None
    relative = image_path.relative_to(input_root)
    if len(relative.parts) >= 2:
        return relative.parts[0]
    return None


def analyze(rows: list[dict]) -> dict:
    confidence_by_group: dict[str, list[float]] = {}
    for row in rows:
        if row["status"] == "recognized" and row["confidence"]:
            confidence_by_group.setdefault(row["group"], []).append(float(row["confidence"]))

    summary = {
        "num_images": len(rows),
        "groups": {},
        "candidate_unknown_threshold": None,
        "threshold_note": (
            "Candidate threshold is exploratory and must not be treated as scientifically "
            "validated without a sufficiently large real-world validation set."
        ),
    }
    for group, values in confidence_by_group.items():
        summary["groups"][group] = {
            "count": len(values),
            "mean_confidence": statistics.mean(values) if values else None,
            "median_confidence": statistics.median(values) if values else None,
            "min_confidence": min(values) if values else None,
            "max_confidence": max(values) if values else None,
        }

    known = confidence_by_group.get("known", [])
    negative = confidence_by_group.get("unknown", []) + confidence_by_group.get("non_food", [])
    if known and negative:
        summary["candidate_unknown_threshold"] = (statistics.median(known) + statistics.median(negative)) / 2
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate real-world food images recursively.")
    parser.add_argument("--input", type=Path, required=True, help="Input folder.")
    parser.add_argument("--checkpoint", type=Path, default=PROJECT_ROOT / "models" / "efficientnet_b0_central_asian_food_v1.pth")
    parser.add_argument("--csv-output", type=Path, default=PROJECT_ROOT / "reports" / "ood_results.csv")
    parser.add_argument("--analysis-output", type=Path, default=PROJECT_ROOT / "reports" / "ood_analysis.json")
    args = parser.parse_args()

    predictor = load_predictor(checkpoint_path=args.checkpoint)
    rows: list[dict] = []
    for image_path in iter_images(args.input):
        group = infer_group(image_path)
        result = predictor.predict_image(image_path, top_k=3)
        ground_truth = infer_ground_truth(args.input, image_path, group)
        correct = ground_truth == result.prediction if ground_truth and result.prediction else None
        rows.append(
            {
                "image_path": str(image_path),
                "group": group,
                "ground_truth": ground_truth,
                "status": result.status,
                "prediction": result.prediction,
                "confidence": result.confidence,
                "top_3": json.dumps([model_to_dict(item) for item in result.top_3]),
                "correct": correct,
                "error": result.error,
            }
        )

    args.csv_output.parent.mkdir(parents=True, exist_ok=True)
    with args.csv_output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "image_path",
                "group",
                "ground_truth",
                "status",
                "prediction",
                "confidence",
                "top_3",
                "correct",
                "error",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    analysis = analyze(rows)
    known_rows = [row for row in rows if row["ground_truth"]]
    if known_rows:
        analysis["known_accuracy"] = sum(1 for row in known_rows if row["correct"]) / len(known_rows)

    with args.analysis_output.open("w", encoding="utf-8") as file:
        json.dump(analysis, file, indent=2)

    print(f"Wrote {args.csv_output}")
    print(f"Wrote {args.analysis_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
