from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from food_classifier.labels import CLASS_NAMES

NUTRITION_TOLERANCE_PCT = 10.0
MACRO_KEYS = ("calories_kcal", "protein_g", "fat_g", "carbohydrates_g")

# Maps a nutrition record slug to the model class names it applies to.
# "coarse" means the classifier separates variants that the nutrition source does not,
# so the same figures are applied to several classes. Those are flagged in the output
# so the app can surface a range rather than a false-precision number.
SLUG_TO_CLASSES: dict[str, list[str]] = {
    "achichuk": ["achichuk"],
    "osh-palov": ["plov"],
    "somsa": ["samsa"],
    "manti": ["manty"],
    "shorva": ["shorpa"],
    "norin": ["naryn"],
    "hasip": ["asip"],
    "lagmon": ["lagman-fried", "lagman-w-soup", "lagman-wo-soup"],
    "chuchvara": ["tushpara-fried", "tushpara-w-soup", "tushpara-wo-soup"],
    "beshbarmoq": ["beshbarmak-w-kazy", "beshbarmak-wo-kazy"],
    "kabob-shashlik": [
        "shashlyk-chicken",
        "shashlyk-chicken-v",
        "shashlyk-kuskovoi",
        "shashlyk-kuskovoi-v",
        "shashlyk-minced-meat",
    ],
    # Added from web research; each was Atwater-validated before inclusion.
    "bauyrsak": ["bauyrsak"],
    "chak-chak": ["chak-chak"],
    "kurt": ["kurt"],
    "kuyrdak": ["kuyrdak"],
    "kazy-karta": ["kazy-karta"],
}

# Deliberately NOT mapped. Each is a real dish with real sourced nutrition, but the
# classifier has no class for it, or the nearest class is a different dish.
#   dimlama, mastava, moshxorda, dolma, qovurilgan-kartoshka, guruch-damlangan,
#   qovurilgan-tuxum, qaynatilgan-tuxum, sut, shirin-choy, baliq-sazan
#     -> no corresponding model class at all.
#   non-patir  -> the model has three distinct flatbreads (taba-nan, kattama-nan,
#                 shelpek) with different fat content; one patir figure would be wrong
#                 for at least two of them.
#   qovurma    -> nearest class kuyrdak is fried offal, a materially different dish.
#   xonim      -> nearest class orama is related but not equivalent.

COARSE_SLUGS = {"lagmon", "chuchvara", "beshbarmoq", "kabob-shashlik"}


def atwater_kcal(macros: dict) -> float:
    return (
        4.0 * macros["protein_g"]
        + 9.0 * macros["fat_g"]
        + 4.0 * macros["carbohydrates_g"]
    )


def check_record(record: dict) -> tuple[bool, str]:
    macros = record.get("nutrition_per_100g") or {}

    missing = [key for key in MACRO_KEYS if macros.get(key) is None]
    if missing:
        return False, f"missing macros: {', '.join(missing)}"

    if not record.get("source_url"):
        return False, "no source_url"

    stated = macros["calories_kcal"]
    if stated <= 0:
        return False, "non-positive calories"

    deviation = abs(atwater_kcal(macros) - stated) / stated * 100.0
    if deviation > NUTRITION_TOLERANCE_PCT:
        return False, f"Atwater mismatch {deviation:.1f}% > {NUTRITION_TOLERANCE_PCT}%"

    return True, f"ok (Atwater deviation {deviation:.1f}%)"


def main() -> int:
    raw_path = PROJECT_ROOT / "nutrition" / "nutrition_raw.json"
    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw records not found: {raw_path}. Place the collected records there."
        )

    raw = json.loads(raw_path.read_text(encoding="utf-8"))

    usable: list[dict] = []
    pending: list[dict] = []
    rejected: list[dict] = []

    for record in raw:
        slug = record["slug"]
        ok, reason = check_record(record)

        if not ok:
            rejected.append({"slug": slug, "reason": reason})
            continue

        classes = SLUG_TO_CLASSES.get(slug, [])
        entry = {
            "slug": slug,
            "name_uz": record.get("name_uz"),
            "name_ru": record.get("name_ru"),
            "name_en": record.get("name_en"),
            "nutrition_per_100g": record["nutrition_per_100g"],
            "source": record.get("source"),
            "source_url": record.get("source_url"),
            "quality_check": reason,
        }

        if classes:
            entry["model_classes"] = sorted(classes)
            entry["granularity"] = "coarse" if slug in COARSE_SLUGS else "exact"
            usable.append(entry)
        else:
            entry["reason_unmapped"] = "no corresponding classifier class"
            pending.append(entry)

    usable.sort(key=lambda item: item["slug"])
    pending.sort(key=lambda item: item["slug"])
    rejected.sort(key=lambda item: item["slug"])

    covered: set[str] = set()
    for entry in usable:
        covered.update(entry["model_classes"])
    uncovered = sorted(set(CLASS_NAMES) - covered)

    output = {
        "version": "v1",
        "units": "per 100 g edible portion",
        "tolerance_pct": NUTRITION_TOLERANCE_PCT,
        "coverage": {
            "model_classes_total": len(CLASS_NAMES),
            "model_classes_covered": len(covered),
            "model_classes_uncovered": len(uncovered),
            "uncovered_classes": uncovered,
        },
        "records": usable,
        "pending_model_coverage": pending,
        "rejected": rejected,
    }

    out_path = PROJECT_ROOT / "nutrition" / "nutrition.json"
    out_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"Wrote {out_path}")
    print(f"  usable records        : {len(usable)}")
    print(f"  pending (no class)    : {len(pending)}")
    print(f"  rejected (bad data)   : {len(rejected)}")
    print(
        f"  class coverage        : {len(covered)}/{len(CLASS_NAMES)} "
        f"({len(covered) / len(CLASS_NAMES):.0%})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
