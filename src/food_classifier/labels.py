from __future__ import annotations

import json
from pathlib import Path


# Recovered from the dataset train folder listing and sorted exactly as the notebook
# computes class_names: sorted(p.name for p in train_split_path.iterdir() if p.is_dir()).
CLASS_NAMES: list[str] = [
    "achichuk",
    "airan-katyk",
    "asip",
    "bauyrsak",
    "beshbarmak-w-kazy",
    "beshbarmak-wo-kazy",
    "chak-chak",
    "cheburek",
    "doner-lavash",
    "doner-nan",
    "hvorost",
    "irimshik",
    "kattama-nan",
    "kazy-karta",
    "kurt",
    "kuyrdak",
    "kymyz-kymyran",
    "lagman-fried",
    "lagman-w-soup",
    "lagman-wo-soup",
    "manty",
    "naryn",
    "nauryz-kozhe",
    "orama",
    "plov",
    "samsa",
    "shashlyk-chicken",
    "shashlyk-chicken-v",
    "shashlyk-kuskovoi",
    "shashlyk-kuskovoi-v",
    "shashlyk-minced-meat",
    "sheep-head",
    "shelpek",
    "shorpa",
    "soup-plain",
    "sushki",
    "suzbe",
    "taba-nan",
    "talkan-zhent",
    "tushpara-fried",
    "tushpara-w-soup",
    "tushpara-wo-soup",
]


def default_class_mapping() -> dict[str, str]:
    return {str(index): name for index, name in enumerate(CLASS_NAMES)}


def load_class_mapping(path: str | Path) -> dict[int, str]:
    mapping_path = Path(path)
    with mapping_path.open("r", encoding="utf-8") as file:
        raw = json.load(file)

    if "idx_to_class" in raw:
        raw = raw["idx_to_class"]

    mapping = {int(index): str(name) for index, name in raw.items()}
    validate_class_mapping(mapping)
    return mapping


def validate_class_mapping(mapping: dict[int, str], expected_num_classes: int = 42) -> None:
    if len(mapping) != expected_num_classes:
        raise ValueError(f"Expected {expected_num_classes} classes, found {len(mapping)}.")

    expected_indices = list(range(expected_num_classes))
    actual_indices = sorted(mapping.keys())
    if actual_indices != expected_indices:
        raise ValueError(
            "Class mapping indices must be continuous from "
            f"0 to {expected_num_classes - 1}; found {actual_indices}."
        )

    names = list(mapping.values())
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"Duplicate class names in mapping: {duplicates}")

    empty = [index for index, name in mapping.items() if not name.strip()]
    if empty:
        raise ValueError(f"Empty class names at indices: {empty}")
