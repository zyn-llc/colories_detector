from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from food_classifier.predictor import load_predictor
from food_classifier.unknown import UnknownPolicy, compute_signals
from food_classifier.validation import ImageValidationError, validate_image_path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
MIN_KNOWN_IMAGES = 20


def iter_images(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            yield path


def group_of(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    if "known" in parts:
        return "known"
    if "non_food" in parts:
        return "non_food"
    if "unknown" in parts:
        return "unknown"
    return "unlabeled"


def percentile(values: list[float], fraction: float) -> float:
    """Lower-bound percentile. fraction=0.05 -> value below which 5% of data sits."""
    if not values:
        raise ValueError("empty sample")
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round(fraction * (len(ordered) - 1)))))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "real_world_test")
    parser.add_argument(
        "--target-false-unknown-rate",
        type=float,
        default=0.05,
        help="Fraction of genuine food photos you accept being marked unknown.",
    )
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report the distributions and proposed policy without writing it.",
    )
    args = parser.parse_args()

    if not 0.0 < args.target_false_unknown_rate < 0.5:
        raise SystemExit("--target-false-unknown-rate must be between 0 and 0.5.")

    if not args.input.exists():
        raise SystemExit(f"Input folder not found: {args.input}")

    predictor = load_predictor(force_reload=True)
    # Calibration must observe the raw model, not a previously calibrated policy.
    predictor.policy = UnknownPolicy.inactive()
    predictor.unknown_threshold = None

    samples: dict[str, list[dict]] = {"known": [], "non_food": [], "unknown": []}
    skipped: list[str] = []

    for image_path in iter_images(args.input):
        group = group_of(image_path)
        if group not in samples:
            continue
        try:
            validated = validate_image_path(image_path)
        except ImageValidationError as exc:
            skipped.append(f"{image_path.name}: {exc}")
            continue

        probabilities = predictor._probabilities(validated.image)
        signals = compute_signals(probabilities[0].cpu().tolist())
        samples[group].append(signals.as_dict())

    print("=" * 62)
    print("SIGNAL DISTRIBUTIONS")
    print("=" * 62)
    for group, rows in samples.items():
        if not rows:
            print(f"{group:10s} no images")
            continue
        print(f"{group:10s} n={len(rows)}")
        for key in ("confidence", "margin", "entropy"):
            values = [row[key] for row in rows]
            print(
                f"    {key:11s} min={min(values):.3f} "
                f"median={statistics.median(values):.3f} max={max(values):.3f}"
            )

    if skipped:
        print(f"\nskipped {len(skipped)} unreadable images")

    known = samples["known"]
    negatives = samples["non_food"] + samples["unknown"]

    if len(known) < MIN_KNOWN_IMAGES:
        print(
            f"\nREFUSING to write a policy: only {len(known)} known-food images, "
            f"need at least {MIN_KNOWN_IMAGES}. A threshold fitted to fewer images "
            "would be noise, not calibration."
        )
        return 1

    rate = args.target_false_unknown_rate
    policy = UnknownPolicy(
        min_confidence=percentile([row["confidence"] for row in known], rate),
        min_margin=percentile([row["margin"] for row in known], rate),
        max_entropy=percentile([row["entropy"] for row in known], 1.0 - rate),
        calibrated_on=(
            f"{len(known)} known, {len(samples['non_food'])} non_food, "
            f"{len(samples['unknown'])} unknown"
        ),
        target_false_unknown_rate=rate,
    )

    print()
    print("=" * 62)
    print("PROPOSED POLICY")
    print("=" * 62)
    print(json.dumps(policy.to_dict(), indent=2))

    # Measure what the policy actually does, rather than assuming it works.
    def rejection_rate(rows: list[dict]) -> float | None:
        if not rows:
            return None
        from food_classifier.unknown import UnknownSignals

        rejected = sum(
            1
            for row in rows
            if policy.evaluate(UnknownSignals(**row))[0]
        )
        return rejected / len(rows)

    print()
    print("MEASURED BEHAVIOUR")
    known_rate = rejection_rate(known)
    print(f"  known food wrongly rejected : {known_rate:.1%}  (target {rate:.0%})")
    for group in ("non_food", "unknown"):
        group_rate = rejection_rate(samples[group])
        if group_rate is None:
            print(f"  {group:26s}: no images supplied, effectiveness UNMEASURED")
        else:
            print(f"  {group:26s}: {group_rate:.1%} correctly rejected")

    if not negatives:
        print(
            "\nWARNING: with no non-food or unknown images, this policy is tuned only "
            "to avoid rejecting real food. Its ability to catch non-food is untested."
        )

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return 0

    written = policy.save(args.output)
    print(f"\nWrote {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
