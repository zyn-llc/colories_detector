# Model Artifacts

## Checkpoint history

### `INVALID_untrained_NOT_finetuned.pth.quarantine` — do not use

Saved by a notebook cell that ran **before** any training loop. Its classifier head is
just PyTorch's default `Linear(1280, 42)` init — fed 8 varied inputs it returns the same
class every time at ~3% confidence, against a 1/42 = 2.38% uniform baseline. Kept around
(quarantined, not loadable by the app) as a reminder of what "the file exists and the app
runs" does not guarantee.

### `best_baseline_stage1.pth` — stage 1, head-only

Classifier head trained for 5 epochs with the EfficientNet-B0 backbone frozen. Val
accuracy 75.14%, val Macro F1 71.18%. Underfit, not overfit — validation accuracy came in
above train accuracy, which is exactly what you'd expect right before unfreezing more of
the backbone.

### `best_efficientnet_b0_finetuned.pth` — stage 2, fine-tuned

The last three EfficientNet feature blocks were unfrozen and trained for 15 more epochs
on top of the stage-1 head. Best epoch 9, best validation Macro F1 84.39%. This is the
checkpoint the production model is built from.

## Current production checkpoint

`efficientnet_b0_central_asian_food_v1.pth` wraps `best_efficientnet_b0_finetuned.pth`
in the production metadata format used by `src/food_classifier/model.py`:

```
version                  = "v1.0"
stage                    = "fine_tuned"
is_final_finetuned_model = True
source_checkpoint        = "best_efficientnet_b0_finetuned.pth"
```

Measured on the 2,698-image held-out test set:

| Metric | Value |
| --- | --- |
| Top-1 accuracy | 86.58% |
| Top-3 accuracy | 96.96% |
| Macro F1 | 84.41% |
| Weighted F1 | 86.46% |

Per-class numbers are in `classification_report.csv`. Regenerate the production
checkpoint from the fine-tuned weights with:

```bash
python scripts/export_model.py --source-checkpoint models/best_efficientnet_b0_finetuned.pth --stage fine_tuned --version v1.0
```

## Class mapping

`class_mapping.json` matches the notebook rule
`sorted(p.name for p in (DATASET_ROOT/"train").iterdir() if p.is_dir())` and is
consistent across `labels.py`, `class_mapping.json`, and the checkpoint's `class_names`.
Verified: index 0 `achichuk`, 24 `plov`, 41 `tushpara-wo-soup`.
