# Notebook Audit

Source inspected: `D:\world bank\nutrition_classification_complete.ipynb`

## Environment

- Notebook format: nbformat 4.5.
- Kernel metadata: Python 3, no Python package versions persisted.
- Executed outputs are persisted only through the stage-1 training cell. Fine-tuning, final test evaluation, report export, and artifact check cells have code but no saved outputs.

## Imports Found

- Data and audit: `os`, `pathlib.Path`, `collections.Counter`, `collections.defaultdict`, `hashlib`, `PIL.Image`, `pandas`, `numpy`.
- Dataset download: `kagglehub`.
- Training: `random`, `torch`, `torch.nn`, `torch.utils.data.Dataset`, `torch.utils.data.DataLoader`, `torchvision.models`, `torchvision.models.EfficientNet_B0_Weights`.
- Image processing: `cv2`, `albumentations`, `albumentations.pytorch.ToTensorV2`.
- Metrics: `sklearn.metrics.accuracy_score`, `sklearn.metrics.f1_score`.
- Later cells reference but do not visibly import: `json`, `matplotlib.pyplot as plt`, `precision_score`, `recall_score`, `classification_report`, `confusion_matrix`.

## Dataset

- Download call: `kagglehub.dataset_download("csdepartmentfood/central-asian-food-dataset")`.
- Notebook dataset root: `DATASET_ROOT = path`, where `path` is the KaggleHub download path.
- Persisted run path: `/root/.cache/kagglehub/datasets/csdepartmentfood/central-asian-food-dataset/versions/1`.
- Splits are existing folders: `train`, `val`, `test`. There is no random split in the notebook.
- Image extensions collected in audit: `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`.
- Persisted counts: train 10969, val 2735, test 2698, total 16402.
- Persisted audit: 0 corrupted images, 0 exact duplicate files, 0 cross-split exact duplicate groups, all images RGB, 725 images smaller than 100x100.

## Class Mapping

The notebook creates one global mapping from training directory names:

```python
class_names = sorted([p.name for p in train_split_path.iterdir() if p.is_dir()])
class_to_idx = {class_name: idx for idx, class_name in enumerate(class_names)}
```

Cell 17 did not persist its printed output. The class names were recovered from the public dataset `train` folder listing and then sorted according to the notebook code.

| Index | Class |
| ---: | --- |
| 0 | achichuk |
| 1 | airan-katyk |
| 2 | asip |
| 3 | bauyrsak |
| 4 | beshbarmak-w-kazy |
| 5 | beshbarmak-wo-kazy |
| 6 | chak-chak |
| 7 | cheburek |
| 8 | doner-lavash |
| 9 | doner-nan |
| 10 | hvorost |
| 11 | irimshik |
| 12 | kattama-nan |
| 13 | kazy-karta |
| 14 | kurt |
| 15 | kuyrdak |
| 16 | kymyz-kymyran |
| 17 | lagman-fried |
| 18 | lagman-w-soup |
| 19 | lagman-wo-soup |
| 20 | manty |
| 21 | naryn |
| 22 | nauryz-kozhe |
| 23 | orama |
| 24 | plov |
| 25 | samsa |
| 26 | shashlyk-chicken |
| 27 | shashlyk-chicken-v |
| 28 | shashlyk-kuskovoi |
| 29 | shashlyk-kuskovoi-v |
| 30 | shashlyk-minced-meat |
| 31 | sheep-head |
| 32 | shelpek |
| 33 | shorpa |
| 34 | soup-plain |
| 35 | sushki |
| 36 | suzbe |
| 37 | taba-nan |
| 38 | talkan-zhent |
| 39 | tushpara-fried |
| 40 | tushpara-w-soup |
| 41 | tushpara-wo-soup |

## Preprocessing

Training transform:

1. `A.LongestMaxSize(max_size=256)`
2. `A.PadIfNeeded(min_height=256, min_width=256, border_mode=cv2.BORDER_CONSTANT)`
3. `A.RandomCrop(224, 224)`
4. `A.HorizontalFlip(p=0.5)`
5. `A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.10, rotate_limit=15, p=0.5)`
6. `A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05, p=0.5)`
7. `A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))`
8. `ToTensorV2()`

Validation, test, and single-image inference transform:

1. `A.LongestMaxSize(max_size=256)`
2. `A.PadIfNeeded(min_height=256, min_width=256, border_mode=cv2.BORDER_CONSTANT)`
3. `A.CenterCrop(224, 224)`
4. `A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))`
5. `ToTensorV2()`

Images are read with OpenCV in the notebook, converted from BGR to RGB, then transformed.

## DataLoader

- Batch size: 32.
- Num workers: 2.
- Train loader: `shuffle=True`, `pin_memory=True`.
- Validation/test loaders: `shuffle=False`, `pin_memory=True`.

## Model

- Architecture: `torchvision.models.efficientnet_b0`.
- Pretrained weights: `EfficientNet_B0_Weights.DEFAULT`.
- Classifier replacement:

```python
model.classifier = nn.Sequential(
    nn.Dropout(0.3),
    nn.Linear(in_features, NUM_CLASSES),
)
```

- Output classes: 42.

## Training Configuration

- Seed: 42.
- cuDNN deterministic: true.
- cuDNN benchmark: false.
- Stage 1: 5 epochs, features frozen, classifier trainable, AdamW, LR 1e-3, weight decay 1e-4, CosineAnnealingLR T_max 5.
- Stage 2: 15 epochs, all features frozen first, final three `model.features[-3:]` blocks unfrozen, classifier trainable, AdamW, LR 1e-4, weight decay 1e-4, CosineAnnealingLR T_max 15.
- Loss: `nn.CrossEntropyLoss()`.
- No label smoothing and no class weights found.
- AMP: `torch.cuda.amp.GradScaler()` and `torch.cuda.amp.autocast()` in training.

## Evaluation

- Validation selection criterion: validation Macro F1.
- Test evaluation uses `torch.softmax(logits, dim=1)`, Top-1 from the first Top-K index, and Top-3 membership check.
- Final classification report and confusion matrix code exists but outputs are not persisted.

## Checkpoints and Artifacts

Configured output directory:

`/content/central_asian_food_model_v1`

Configured artifacts:

- `best_baseline_stage1.pth`
- `best_efficientnet_b0_finetuned.pth`
- `efficientnet_b0_central_asian_food_v1.pth`
- `class_mapping.json`
- `model_config.json`
- `metrics.json`
- `classification_report.csv`

No checkpoint or exported artifact was found next to the local notebook in `D:\world bank`.

Important unresolved checkpoint issue: the persisted stage-1 save cell writes a raw `model.state_dict()` to `"best_baseline_stage1.pth"` relative to the current directory, while the stage-2 load cell reads `BEST_STAGE1_PATH` under `/content/central_asian_food_model_v1` and expects `stage1_checkpoint["model_state_dict"]`. The successful run may have used a different intermediate state, but that cannot be verified from the saved notebook file.

## Reported Metrics

The request text reports these final metrics, but the inspected notebook file does not persist the final evaluation output:

- Test Top-1 Accuracy: 86.1749%.
- Test Top-3 Accuracy: 96.7383%.
- Test Macro F1: approximately 83.84%.
- Test Weighted F1: approximately 86.07%.
- Best validation accuracy: approximately 84.75%.
- Best validation Macro F1: approximately 82.74%.
- Best checkpoint: around epoch 14.

## Unresolved Issues

- Final `.pth` checkpoint is not locally available.
- Fine-tuning outputs and final test outputs are not saved in the notebook file.
- Exact final classification report values and weak-class metrics cannot be verified from the notebook file.
- Several imports needed by later cells are not visible in the saved notebook.
- The original notebook could not be copied into this output folder because runtime file-copy operations were blocked by the sandbox; the inspected notebook remains at the absolute source path above.
