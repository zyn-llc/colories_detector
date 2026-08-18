"""Join classifier output to display names and nutrition facts.

This is strictly a lookup layer over the model. The classifier emits an index, the
index maps to a frozen dataset slug via class_mapping.json, and this module attaches
the Uzbek/Russian/English names and the nutrition record to that slug.

Nothing here changes model behaviour, and no nutrition value is ever synthesised: a
dish with no sourced record returns coverage="none" so the caller can say "no data"
instead of showing a fabricated number.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from food_classifier.config import PROJECT_ROOT


CATALOG_PATH = PROJECT_ROOT / "nutrition" / "class_catalog.json"
NUTRITION_PATH = PROJECT_ROOT / "nutrition" / "nutrition.json"


@dataclass(frozen=True)
class FoodInfo:
    """Everything the app needs to render one predicted class."""

    class_name: str
    name_uz: str
    name_ru: str
    name_en: str
    origin: str
    uz_name_type: str
    status: str
    #: "exact"   - nutrition sourced for this dish specifically
    #: "coarse"  - sourced for a dish family; the model separates variants the
    #:             nutrition source does not, so treat the figures as approximate
    #: "none"    - no sourced record; callers must not display calories
    coverage: str = "none"
    nutrition_per_100g: dict | None = None
    source: str | None = None
    source_url: str | None = None

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def has_nutrition(self) -> bool:
        return self.coverage != "none" and self.nutrition_per_100g is not None

    def calories_for_grams(self, grams: float) -> float | None:
        """Scale energy to a portion. Returns None when no record exists."""
        if not self.has_nutrition:
            return None
        if grams <= 0:
            raise ValueError("grams must be positive.")
        return self.nutrition_per_100g["calories_kcal"] * grams / 100.0

    def macros_for_grams(self, grams: float) -> dict | None:
        if not self.has_nutrition:
            return None
        if grams <= 0:
            raise ValueError("grams must be positive.")
        factor = grams / 100.0
        return {
            key: round(value * factor, 1)
            for key, value in self.nutrition_per_100g.items()
        }


class NutritionLookupError(RuntimeError):
    """Raised when the catalog and the model class list disagree."""


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, FoodInfo]:
    """Build the class_name -> FoodInfo table. Cached; call cache_clear() after edits."""
    if not CATALOG_PATH.exists():
        raise NutritionLookupError(f"Class catalog not found: {CATALOG_PATH}")

    catalog_raw = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    records: dict[str, dict] = {}
    if NUTRITION_PATH.exists():
        nutrition_raw = json.loads(NUTRITION_PATH.read_text(encoding="utf-8"))
        for record in nutrition_raw.get("records", []):
            records[record["slug"]] = record

    table: dict[str, FoodInfo] = {}
    for entry in catalog_raw["classes"]:
        slug = entry.get("nutrition_slug")
        record = records.get(slug) if slug else None

        coverage = "none"
        macros = None
        source = None
        source_url = None
        if record is not None:
            coverage = record.get("granularity", "exact")
            macros = record["nutrition_per_100g"]
            source = record.get("source")
            source_url = record.get("source_url")

        table[entry["class_name"]] = FoodInfo(
            class_name=entry["class_name"],
            name_uz=entry["name_uz"],
            name_ru=entry["name_ru"],
            name_en=entry["name_en"],
            origin=entry["origin"],
            uz_name_type=entry["uz_name_type"],
            status=entry["status"],
            coverage=coverage,
            nutrition_per_100g=macros,
            source=source,
            source_url=source_url,
        )

    return table


def get_food_info(class_name: str) -> FoodInfo:
    table = load_catalog()
    if class_name not in table:
        raise NutritionLookupError(
            f"Class '{class_name}' is not in the catalog. "
            "Every model class must have a catalog entry."
        )
    return table[class_name]


def validate_catalog_against_model(class_names: list[str]) -> None:
    """Fail loudly if the catalog and the checkpoint's class list have drifted apart."""
    table = load_catalog()
    missing = [name for name in class_names if name not in table]
    extra = [name for name in table if name not in class_names]
    if missing or extra:
        raise NutritionLookupError(
            f"Catalog/model mismatch. Missing from catalog: {missing}. "
            f"Not in model: {extra}."
        )


def coverage_summary() -> dict:
    table = load_catalog()
    active = [info for info in table.values() if info.is_active]
    return {
        "classes_total": len(table),
        "classes_active": len(active),
        "classes_hidden": len(table) - len(active),
        "with_nutrition": sum(1 for info in active if info.has_nutrition),
        "exact": sum(1 for info in active if info.coverage == "exact"),
        "coarse": sum(1 for info in active if info.coverage == "coarse"),
        "missing_nutrition": sorted(
            info.class_name for info in active if not info.has_nutrition
        ),
    }
