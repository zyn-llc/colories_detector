# Deploying to Streamlit Community Cloud

The demo runs locally with `streamlit run app/streamlit_app.py`. Publishing it needs
three things fixed that would otherwise fail the build. All three are already done in
this repository; this document records what and why.

## What was fixed for deployment

### 1. The checkpoint must be committed

`.gitignore` excluded `models/*.pth`. Streamlit Community Cloud builds **only from the
git repository** — it has no access to your D: drive — so an ignored checkpoint means
the deployed app raises `ModelLoadError: Checkpoint not found`.

`models/efficientnet_b0_central_asian_food_v1.pth` is 16 MB, well under GitHub's 100 MB
per-file limit, so it is now explicitly un-ignored:

```gitignore
models/*.pth
!models/efficientnet_b0_central_asian_food_v1.pth
```

Confirm it is actually tracked before deploying:

```bash
git check-ignore -v models/efficientnet_b0_central_asian_food_v1.pth
```

No output means it is tracked. If it prints a rule, it is still ignored.

### 2. CPU-only PyTorch

Plain `torch` in `requirements.txt` pulls the CUDA build (~2.5 GB), which exceeds the
Community Cloud image budget and fails the build. `requirements.txt` now starts with:

```
--extra-index-url https://download.pytorch.org/whl/cpu
```

which serves the ~200 MB CPU wheels. The app runs on CPU anyway — inference on one
224x224 image is well under a second.

### 3. `opencv-python-headless`, not `opencv-python`

Community Cloud's Linux image has no `libGL`, so `opencv-python` fails at import with:

```
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

The headless wheel is identical minus the GUI bindings, which the app never uses.

### Runtime vs development dependencies

`requirements.txt` now holds only what the deployed app imports. Training and testing
extras (`pytest`, `pandas`, `scikit-learn`, `matplotlib`, `kagglehub`) moved to
`requirements-dev.txt`. Keeping them out of the runtime file is part of what keeps the
image inside its size budget.

Local development:

```bash
pip install -r requirements-dev.txt
```

## Deploy steps

1. Push the repository to GitHub, including the checkpoint:

   ```bash
   git add models/efficientnet_b0_central_asian_food_v1.pth
   git commit -m "Add production checkpoint for deployment"
   git push
   ```

2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.

3. **New app** → pick the repository and branch, then set:

   | Field | Value |
   | --- | --- |
   | Main file path | `app/streamlit_app.py` |
   | Python version | 3.10 or later |

4. Deploy. The first build takes several minutes, mostly downloading torch.

No secrets are needed — the app has no API keys or database.

## Notes

**Theme.** `.streamlit/config.toml` is committed, so the deployed app picks up the same
theme automatically. Streamlit resolves it relative to the working directory, which is
why running locally from a different folder loses the styling — always run from the
project root.

**Cold starts.** Community Cloud sleeps idle apps. The first request after a sleep
reloads the checkpoint, which `@st.cache_resource` then holds for the life of the
process. Open the app a few minutes before demoing it.

**Memory.** EfficientNet-B0 in float32 is ~21 MB of weights; total process footprint
with torch is roughly 400-600 MB, inside the free tier's 1 GB.

**Repository size.** If you later commit several checkpoints, move them to Git LFS —
GitHub warns above 50 MB per file and every clone pays for the history.
