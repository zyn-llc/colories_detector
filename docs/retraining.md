# Retraining: recovering `best_efficientnet_b0_finetuned.pth`

The stage-2 fine-tuned checkpoint does not exist and cannot be recovered from any file
in this workspace. It must be retrained. The notebook remains the source of truth; this
document lists the **minimum patches** needed to make its stage-2 cells actually run,
plus the changes that address poor generalization to new photos.

Run in Colab with a GPU. Stage 1 (5 epochs) + stage 2 (15 epochs) on ~11k training
images is roughly 30-50 minutes on a T4.

---

## Part A — two bugs that block stage 2

### Bug 1: cell 11 never executed

Cell 11 defines `OUTPUT_DIR`, `BEST_STAGE1_PATH`, `BEST_FINETUNED_PATH`,
`PRODUCTION_MODEL_PATH`, `CLASS_MAPPING_PATH`, `CONFIG_PATH`, `METRICS_PATH`,
`REPORT_PATH`. It has `execution_count: null`. Every later cell that references those
names raises `NameError`.

It also reads `NUM_CLASSES = len(class_names)` at line 6, but `class_names` is not
defined until **cell 17**. So cell 11 cannot run in its current position.

**Fix:** move cell 11 to run *after* cell 17, or delete the `NUM_CLASSES` line from
cell 11 (cell 17 already sets it). Then run cell 11 before cell 32.

### Bug 2: stage-1 checkpoint format mismatch

Cell 32 saves a bare state dict to a relative filename:

```python
torch.save(model.state_dict(), "best_baseline_stage1.pth")
```

Cell 34 expects a wrapped dict at an absolute path:

```python
stage1_checkpoint = torch.load(BEST_STAGE1_PATH, map_location=DEVICE)
model.load_state_dict(stage1_checkpoint["model_state_dict"])   # KeyError
```

**Fix — change the save in cell 32 to match the load in cell 34:**

```python
torch.save(
    {
        "model_state_dict": model.state_dict(),
        "stage": "stage1_head_only",
        "best_val_f1": best_f1,
        "best_epoch": epoch + 1,
    },
    BEST_STAGE1_PATH,
)
```

### Also: delete cell 31

```python
torch.save(model.state_dict(), "best_baseline.pth")   # DELETE THIS CELL
```

It runs before any training and writes an untrained random-head checkpoint. This is the
file the app was serving. It has no legitimate use.

### Also: add the missing imports

Cells 38-46 use names never imported in the notebook. Add before cell 36:

```python
import json
import matplotlib.pyplot as plt
from sklearn.metrics import (
    precision_score,
    recall_score,
    classification_report,
    confusion_matrix,
)
```

---

## Part B — run order

With Part A applied, execute in this order:

| Cells | What |
| --- | --- |
| 1-9 | Dataset download + integrity audit |
| 10, 12-30 | Config, transforms, dataset, loaders, model, optimizer |
| 17 | Class mapping (**must** run before cell 11) |
| 11 | Paths and seeds |
| 32 | Stage 1 — head only, 5 epochs |
| 34-36 | Stage 2 — fine-tune last 3 feature blocks, 15 epochs |
| 38-48 | Curves, test evaluation, per-class report, confusion matrix |
| 54, 56 | Export production artifacts |

Cell 36 writes `best_efficientnet_b0_finetuned.pth`. Cell 54 writes
`efficientnet_b0_central_asian_food_v1.pth`, `class_mapping.json`, `model_config.json`,
and `metrics.json`.

Expected gain from stage 2: stage 1 plateaued at val Macro F1 0.7118 with **validation
accuracy above train accuracy** — the model is underfit, not overfit. Unfreezing the
last three blocks is exactly the right next step.

---

## Part C — the "good on my data, trash on new photos" problem

This is domain shift, not overfitting. The dataset images are web/studio photos; your
phone photos differ in lighting, angle, plating, and background. Stage 1 numbers rule
out overfitting outright (val > train). Apply these **in addition to** Part A/B:

1. **Fine-tune more of the backbone.** Cell 34 unfreezes `model.features[-3:]`. If
   stage-2 val Macro F1 is still under ~0.85, unfreeze everything with a discriminative
   learning rate:

   ```python
   for param in model.parameters():
       param.requires_grad = True

   optimizer = torch.optim.AdamW(
       [
           {"params": model.features.parameters(),   "lr": 1e-5},
           {"params": model.classifier.parameters(), "lr": 1e-4},
       ],
       weight_decay=WEIGHT_DECAY,
   )
   ```

2. **Stronger augmentation** in `train_transform` (cell 13). The current jitter is mild
   relative to real phone photos. Add after `ShiftScaleRotate`:

   ```python
   A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=0.5),
   A.MotionBlur(blur_limit=5, p=0.2),
   A.ImageCompression(quality_range=(50, 95), p=0.3),
   A.Perspective(scale=(0.02, 0.06), p=0.3),
   ```

3. **Label smoothing** — helps calibration, which matters for the later OOD work:

   ```python
   criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
   ```

4. **Collect a real-world holdout.** Put 10-20 of your own phone photos per class into
   `real_world_test/known/<class_name>/` and run
   `python scripts/evaluate_real_world.py --input real_world_test`. This is the only
   number that predicts app behaviour. Dataset test accuracy will overstate it.

5. **Do not add an OOD threshold yet.** Pick it from the confidence distributions that
   `evaluate_real_world.py` produces once real known / unknown / non-food images exist.

---

## Part D — export into this project

Download `best_efficientnet_b0_finetuned.pth` from Colab, then:

```bash
python scripts/export_model.py --source-checkpoint path/to/best_efficientnet_b0_finetuned.pth --stage fine_tuned --version v1.0
```

Replace `models/metrics.json` with the notebook-generated one first, so the real test
metrics get embedded in the checkpoint rather than the stage-1 placeholders.

Then confirm:

```bash
pytest
```

The two currently-skipped tests (`test_checkpoint_loads_when_available`,
`test_prediction_returns_top1_and_top3_when_checkpoint_available`) will execute once
`models/efficientnet_b0_central_asian_food_v1.pth` is present.
