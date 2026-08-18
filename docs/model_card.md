# Model Card

## Model Name

Central Asian Food EfficientNet-B0 v1.0.

## Architecture

Torchvision EfficientNet-B0 with ImageNet default weights and a replaced classifier:

`Dropout(0.3) -> Linear(in_features, 42)`.

## Classes

The model predicts 42 Central Asian food classes. The output index mapping is stored in `models/class_mapping.json`.

## Dataset

The notebook downloads `csdepartmentfood/central-asian-food-dataset` through KaggleHub and uses existing `train`, `val`, and `test` folders. The persisted audit shows 16402 total images: 10969 train, 2735 validation, and 2698 test.

## Training Method

Stage 1 freezes the EfficientNet feature extractor and trains only the classifier for 5 epochs. Stage 2 unfreezes the final three EfficientNet feature blocks and the classifier for 15 fine-tuning epochs. Model selection is based on validation Macro F1.

## Preprocessing

Inference uses the notebook validation/test transform exactly:

1. Longest side resized to 256.
2. Pad to at least 256x256 with OpenCV constant border.
3. Center crop to 224x224.
4. Normalize with ImageNet mean `[0.485, 0.456, 0.406]` and std `[0.229, 0.224, 0.225]`.
5. Convert to tensor.

No random augmentation is used for inference.

## Evaluation Metrics

### Measured (stage 1, head-only)

Verbatim from the persisted stdout of notebook cell 32. The EfficientNet-B0 backbone
was frozen; only the classifier head was trained, for 5 epochs. Best epoch: 5.

- Validation accuracy: 75.14%.
- Validation Macro F1: 71.18%.
- Train accuracy: 73.78%; train Macro F1: 72.01%.
- Test Top-1 / Top-3 / Macro F1 / Weighted F1: **not measured.**

Validation accuracy exceeding train accuracy indicates the model is *underfit*, not
overfit. Stage 2 (backbone fine-tuning) was never run.

### Unverified — must not be cited

These figures appear in the original request text only. They are not recoverable from
the notebook and no checkpoint in this repository produces them:

- Test Top-1 86.1749%, Test Top-3 96.7383%, Macro F1 ~83.84%, Weighted F1 ~86.07%.

Any checkpoint or metrics file asserting these numbers as measured is mislabeled.

## Known Limitations

- The current repository does not include the trained checkpoint.
- OOD and non-food rejection are not calibrated yet.
- The model assumes one primary dish per image.
- It is not an object detector, segmenter, portion estimator, or nutrition estimator.

## Difficult Classes

The notebook explicitly flags these classes for inspection:

- asip
- shashlyk-chicken
- shashlyk-kuskovoi
- shashlyk-chicken-v
- shashlyk-kuskovoi-v
- shashlyk-minced-meat
- beshbarmak-w-kazy
- beshbarmak-wo-kazy

Exact per-class metrics are unavailable because the classification report output is not saved in the notebook.

## Intended Use

Single-image recognition for the 42 supported Central Asian food classes, returning Top-1 and Top-3 predictions.

## Out-of-Scope Use

- Medical diagnosis or dietary advice.
- Nutrition calculation without a verified nutrition database.
- Unknown-food or non-food detection without real-world threshold calibration.
- Multi-dish scene parsing.

## Reproducibility

Rerun the notebook or recover the fine-tuned checkpoint, then export:

```bash
python scripts/export_model.py --source-checkpoint path/to/best_efficientnet_b0_finetuned.pth
```
