# Central Asian Food AI

An image classifier for Central Asian dishes, plus a calorie/macro lookup on top of it.
Upload a photo, the model tells you what it thinks it is, and if that dish has
verified nutrition data, you get calories and macros scaled to your portion.

It started as a notebook (`nutrition_classification_complete.ipynb`) trained on the
[Central Asian Food Dataset](https://www.kaggle.com/datasets/csdepartmentfood/central-asian-food-dataset)
from Kaggle. This repo is the inference side of it: model loading, preprocessing,
prediction, nutrition lookup, and a small Streamlit demo on top.

## The short version

- **Model**: EfficientNet-B0, fine-tuned in two stages (frozen backbone, then the last
  three feature blocks unfrozen) on 42 Central Asian dish classes.
- **Accuracy**: 86.58% top-1 on a held-out test set of 2,698 images the model never
  trained on. Macro F1 84.41%.
- **Nutrition**: 25 of the 42 classes have calorie/macro data backed by a real source
  URL, checked against the Atwater energy formula before being trusted. The other 17
  are shown as "not recognized" rather than guessed at.
- **Languages**: Uzbek, English, Russian.

## Why this exists

Most food-recognition demos are trained on Western food datasets and have never seen
a plate of plov, manti, or lagman. This one has — it's trained specifically on Central
Asian cuisine, which is a genuinely underserved corner of computer vision.

## A note on how this model got here

The first checkpoint this project shipped with was, it turned out, never actually
trained — a save call had fired before the training loop ran, so the file was just a
randomly initialized classifier head wearing a trained model's filename. It answered
every image with the same class at roughly random-chance confidence. That's documented
in `models/README.md` because it's a useful cautionary tale: **the app can be running,
loading a real checkpoint, and returning confident-looking predictions, and still be
completely wrong**, if nobody checks that the checkpoint was actually trained.

The current model (`v1.0`, `stage: fine_tuned`) doesn't have that problem — its
provenance, every reported metric, and the checkpoint's own metadata are checked
against each other in `docs/notebook_audit.md` and `models/README.md`. Those two files
are the ones worth reading if you're evaluating the project rather than just running it.

## Running it locally

```bash
python -m venv .venv
.venv\Scripts\activate          # .venv/bin/activate on macOS/Linux
pip install -r requirements-dev.txt
streamlit run app/streamlit_app.py
```

Upload a clear photo of one dish. You get a prediction, a confidence score, and — if
the dish has sourced nutrition data — calories and macros for whatever portion size
you set in the sidebar.

## Why there are two requirements files

`requirements.txt` is exactly what `app/streamlit_app.py` imports at runtime: torch
(CPU build), streamlit, Pillow, numpy, albumentations, opencv (headless). That's also
what a Streamlit Community Cloud deploy installs, and it has to stay minimal — the
default CUDA torch wheel alone blows the build past the platform's size limit.

`requirements-dev.txt` adds `-r requirements.txt` plus pytest, pandas, scikit-learn,
matplotlib, and kagglehub — everything the notebook and the test suite need that the
deployed app doesn't. If you're only ever running things locally, `requirements-dev.txt`
is the one to install; the split only matters at deploy time. See `docs/deployment.md`
for the two other non-obvious deploy fixes in there (checkpoint must be committed to
the repo, OpenCV must be the headless build).

## Other ways to run inference

```bash
python scripts/predict.py path/to/image.jpg
```

## Testing

```bash
pytest
```

12 tests, one skipped (it needs a CUDA GPU, which most dev machines don't have). The
two checkpoint-dependent tests run for real once `models/efficientnet_b0_central_asian_food_v1.pth`
is in place.

## What "unknown" means here

If you upload a photo of something that isn't food, or isn't one of the 42 trained
classes, the app is supposed to say so instead of confidently naming the wrong dish.
That rejection isn't hardcoded — there's no `if confidence < 0.6` guess anywhere.
`scripts/calibrate_unknown.py` derives the actual threshold from labelled example
photos (known dishes, non-food, dishes outside the 42 classes) and refuses to write a
policy at all if it doesn't have at least 20 labelled photos to work from. Until
someone runs it with real photos, unknown-rejection stays off rather than shipping a
guessed number.

## Project layout

```text
food-ai/
  app/streamlit_app.py  Demo: upload -> prediction -> nutrition
  docs/                 Model audit, deployment notes, retraining instructions
  models/               Checkpoint, class mapping, metrics, forensic writeup
  nutrition/            Sourced nutrition records + the class -> nutrition catalog
  notebooks/original/   The training notebook this whole project is built from
  real_world_test/      Where to drop real photos for calibration/evaluation
  scripts/              export_model.py, calibrate_unknown.py, evaluate_real_world.py, predict.py
  src/food_classifier/  Model loading, preprocessing, prediction, nutrition lookup
  tests/
```

## Known limitations

- **Five shashlik variants and three lagman variants are genuinely hard to tell
  apart** — even for a person, from a single photo. That's most of the model's
  remaining error; see the per-class breakdown in `models/classification_report.csv`.
- **`asip` has the weakest score** (F1 0.385) because it has the fewest training
  images of any class. More data would help; better training would not.
- **17 of 42 classes have no nutrition data** because no source I found agreed with
  itself (a stated calorie count that doesn't match its own macros isn't data, it's
  noise) or existed at all for that specific dish. They're hidden from the app rather
  than shown with an invented number.
- **One dish per photo.** It's a classifier, not a detector — a plate with three
  different dishes on it gets one label.
- **This is nutrition information, not medical advice.**

## Roadmap

The model and the nutrition lookup both work now. What's left is mostly data:
collecting real phone photos to calibrate unknown-rejection against, and sourcing
nutrition for the remaining 17 dishes from somewhere more reliable than aggregator
websites that disagree with themselves.

## License

MIT — see `LICENSE`.
