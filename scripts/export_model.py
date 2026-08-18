from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from food_classifier.config import DEFAULT_MODEL_CONFIG
from food_classifier.labels import CLASS_NAMES, validate_class_mapping
from food_classifier.model import build_model, validate_model_output_dim


def discover_classes(dataset_root: Path | None) -> list[str]:
    if dataset_root is None:
        return CLASS_NAMES
    train_path = dataset_root / "train"
    if not train_path.exists():
        raise FileNotFoundError(f"Dataset train folder not found: {train_path}")
    class_names = sorted(path.name for path in train_path.iterdir() if path.is_dir())
    validate_class_mapping({index: name for index, name in enumerate(class_names)})
    return class_names


def load_metrics(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    if not path.exists():
        raise FileNotFoundError(f"Metrics file not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Wrap a notebook-generated EfficientNet-B0 checkpoint into the production "
            "checkpoint format. This script does not invent or retrain weights."
        )
    )
    parser.add_argument(
        "--source-checkpoint",
        type=Path,
        required=True,
        help="Path to best_efficientnet_b0_finetuned.pth or an equivalent notebook checkpoint.",
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=None,
        help="Optional dataset root containing train/val/test folders for class discovery.",
    )
    parser.add_argument(
        "--metrics",
        type=Path,
        default=PROJECT_ROOT / "models" / "metrics.json",
        help="Optional metrics JSON to include in the checkpoint metadata.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "models" / "efficientnet_b0_central_asian_food_v1.pth",
    )
    parser.add_argument(
        "--stage",
        default=None,
        help=(
            "Training stage label recorded in the checkpoint, e.g. 'stage1_head_only' "
            "or 'fine_tuned'. Overrides any stage present in the source checkpoint."
        ),
    )
    parser.add_argument(
        "--version",
        default=None,
        help="Version string recorded in the checkpoint. Defaults to the project config version.",
    )
    args = parser.parse_args()

    import torch

    if not args.source_checkpoint.exists():
        raise FileNotFoundError(
            f"Source checkpoint not found: {args.source_checkpoint}. "
            "Rerun the notebook export cells or provide the saved fine-tuned checkpoint."
        )

    class_names = discover_classes(args.dataset_root)
    config = DEFAULT_MODEL_CONFIG
    model = build_model(config=config, pretrained=False)
    validate_model_output_dim(model, len(class_names))

    source = torch.load(args.source_checkpoint, map_location="cpu")
    state_dict = source.get("model_state_dict", source) if isinstance(source, dict) else source
    model.load_state_dict(state_dict)
    model.eval()

    metrics = load_metrics(args.metrics if args.metrics.exists() else None)
    production_checkpoint = {
        "model_state_dict": model.state_dict(),
        "model_name": config.model_name,
        "num_classes": len(class_names),
        "class_names": class_names,
        "class_to_idx": {name: index for index, name in enumerate(class_names)},
        "image_size": config.image_size,
        "normalization": {
            "mean": list(config.normalization_mean),
            "std": list(config.normalization_std),
        },
        "version": args.version or config.version,
        "metrics": metrics,
        "source_checkpoint": args.source_checkpoint.name,
    }
    if isinstance(source, dict):
        for key in ("best_val_f1", "best_epoch", "stage"):
            if key in source:
                production_checkpoint[key] = source[key]
    if args.stage is not None:
        production_checkpoint["stage"] = args.stage
        production_checkpoint["is_final_finetuned_model"] = args.stage == "fine_tuned"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(production_checkpoint, args.output)
    print(f"Saved production checkpoint: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
