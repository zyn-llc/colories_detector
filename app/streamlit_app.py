from __future__ import annotations

import sys
import time
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from food_classifier.i18n import DEFAULT_LANGUAGE, LANGUAGES, dish_name, t
from food_classifier.nutrition import coverage_summary, get_food_info
from food_classifier.predictor import load_predictor


st.set_page_config(page_title="Central Asian Food AI", page_icon=":material/restaurant:")


@st.cache_resource(show_spinner=False)
def get_predictor():
    """Loading the checkpoint costs ~2s, so hold one instance per server process."""
    return load_predictor()


@st.cache_data(show_spinner=False)
def get_coverage():
    return coverage_summary()


# --- Sidebar: language, portion, model stats ---------------------------------

with st.sidebar:
    st.subheader(t("settings", DEFAULT_LANGUAGE))

    _stored = st.session_state.get("language_choice")
    lang = LANGUAGES.get(_stored or list(LANGUAGES)[0], DEFAULT_LANGUAGE)

    st.segmented_control(
        t("language", lang),
        options=list(LANGUAGES),
        default=list(LANGUAGES)[0],
        key="language_choice",
    )

    grams = st.number_input(
        t("portion", lang), min_value=10, max_value=2000, value=250, step=10
    )

    st.divider()
    coverage = get_coverage()
    predictor = get_predictor()
    st.caption(f"{t('classes_label', lang)}: **{coverage['classes_active']}**")
    st.caption(
        f"{t('accuracy_label', lang)}: "
        f"**{predictor.checkpoint['metrics']['top1_accuracy'] * 100:.1f}%** top-1"
    )


# --- Header ------------------------------------------------------------------

st.title(t("app_title", lang))
st.caption(t("app_subtitle", lang))

uploaded = st.file_uploader(
    t("upload", lang),
    type=["jpg", "jpeg", "png", "webp"],
    help=t("upload_help", lang),
)

if uploaded is None:
    st.info(t("waiting", lang), icon=":material/photo_camera:")
    st.stop()


# --- Inference -----------------------------------------------------------

data = uploaded.read()

# Staged progress: each label is shown while its corresponding real step runs
# (recognizing = the actual forward pass, estimating = the actual nutrition
# lookup). Only short cosmetic pauses are added around the near-instant steps
# so the text is legible instead of flashing by.
stage = st.empty()

try:
    stage.caption(t("loading_uploading", lang))
    time.sleep(0.1)

    stage.caption(t("loading_recognizing", lang))
    result = predictor.predict_bytes(data, top_k=1)

    stage.caption(t("loading_estimating", lang))
    info = get_food_info(result.prediction) if result.prediction else None
    time.sleep(0.1)
except Exception as exc:
    stage.empty()
    st.error(t("network_error", lang), icon=":material/error:")
    st.caption(str(exc))
    st.stop()

stage.empty()

image_column, result_column = st.columns([1, 1], gap="medium")

with image_column:
    st.image(data, width="stretch")

if result.status == "invalid_input":
    with result_column:
        st.error(result.error or t("unsupported_format", lang), icon=":material/error:")
    st.stop()

# Hiding a class is a display decision only: the network still emits all 42
# outputs. A hidden top-1 is reported as unknown rather than shown without
# verified nutrition data.
if result.status == "unknown" or info is None or not info.is_active:
    with result_column:
        with st.container(border=True):
            st.subheader(t("unknown_title", lang))
            st.badge(
                f"{(result.confidence or 0.0) * 100:.1f}%",
                icon=":material/help:",
                color="orange",
            )
            reason = (
                t("unknown_hidden", lang)
                if info is not None and not info.is_active
                else t("recognition_failure", lang)
            )
            st.write(reason)
    st.stop()


# --- Result ------------------------------------------------------------------

with result_column:
    with st.container(border=True):
        st.caption(t("dish", lang))
        st.subheader(dish_name(info, lang))
        st.badge(
            f"{t('confidence', lang)} {(result.confidence or 0.0) * 100:.1f}%",
            icon=":material/check_circle:",
            color="green",
        )

st.subheader(t("nutrition", lang))

macros = info.macros_for_grams(grams)
per_100g = info.nutrition_per_100g

with st.container(border=True):
    st.metric(
        f"{t('calories', lang)} · {grams} g",
        f"{macros['calories_kcal']:.0f} kcal",
        delta=f"{per_100g['calories_kcal']:.0f} kcal {t('per_100g', lang)}",
        delta_color="off",
    )
    protein, fat, carbs = st.columns(3)
    protein.metric(t("protein", lang), f"{macros['protein_g']:.1f} g")
    fat.metric(t("fat", lang), f"{macros['fat_g']:.1f} g")
    carbs.metric(t("carbs", lang), f"{macros['carbohydrates_g']:.1f} g")

if info.coverage == "coarse":
    st.warning(t("coarse_warning", lang), icon=":material/info:")
if info.source_url:
    st.caption(f"{t('source', lang)}: [{info.source}]({info.source_url})")

st.divider()

footer = f"{t('model_label', lang)}: EfficientNet-B0 · {result.model_version}"
policy = getattr(predictor, "policy", None)
if (policy is None or not policy.is_active) and predictor.unknown_threshold is None:
    footer += f" · {t('uncalibrated', lang)}"
st.caption(footer)
