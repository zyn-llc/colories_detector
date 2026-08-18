"""Interface strings for the demo app.

Dish names come from nutrition/class_catalog.json (name_uz / name_ru / name_en); this
module only covers the surrounding interface. Adding a language means adding one key
to LANGUAGES and one column to STRINGS -- no other file changes.
"""

from __future__ import annotations



LANGUAGES: dict[str, str] = {
    "O'zbekcha": "uz",
    "English": "en",
    "Русский": "ru",
}

DEFAULT_LANGUAGE = "uz"

#: Catalog field holding the dish name for each language code.
NAME_FIELD: dict[str, str] = {
    "uz": "name_uz",
    "en": "name_en",
    "ru": "name_ru",
}

STRINGS: dict[str, dict[str, str]] = {
    "app_title": {
        "uz": "Markaziy Osiyo taomlari AI",
        "en": "Central Asian Food AI",
        "ru": "Central Asian Food AI",
    },
    "app_subtitle": {
        "uz": "Taom rasmini yuklang — model uni aniqlaydi va kaloriyasini hisoblaydi.",
        "en": "Upload a dish photo — the model identifies it and computes its calories.",
        "ru": "Загрузите фото блюда — модель распознает его и рассчитает калорийность.",
    },
    "settings": {"uz": "Sozlamalar", "en": "Settings", "ru": "Настройки"},
    "language": {"uz": "Til", "en": "Language", "ru": "Язык"},
    "upload": {"uz": "Rasm yuklang", "en": "Upload an image", "ru": "Загрузите изображение"},
    "upload_help": {
        "uz": "JPG, PNG yoki WEBP. Taom aniq ko'rinib turgan rasm eng yaxshi natija beradi.",
        "en": "JPG, PNG or WEBP. A clear, well-lit photo of a single dish works best.",
        "ru": "JPG, PNG или WEBP. Лучше всего работает четкое фото одного блюда.",
    },
    "dish": {"uz": "Taom", "en": "Dish", "ru": "Блюдо"},
    "confidence": {"uz": "Ishonch", "en": "Confidence", "ru": "Уверенность"},
    "nutrition": {"uz": "Ozuqaviy qiymat", "en": "Nutrition", "ru": "Пищевая ценность"},
    "portion": {"uz": "Portsiya (gramm)", "en": "Portion (grams)", "ru": "Порция (граммы)"},
    "calories": {"uz": "Kaloriya", "en": "Calories", "ru": "Калории"},
    "protein": {"uz": "Oqsil", "en": "Protein", "ru": "Белки"},
    "fat": {"uz": "Yog'", "en": "Fat", "ru": "Жиры"},
    "carbs": {"uz": "Uglevod", "en": "Carbs", "ru": "Углеводы"},
    "per_100g": {"uz": "100 g uchun", "en": "per 100 g", "ru": "на 100 г"},
    "source": {"uz": "Manba", "en": "Source", "ru": "Источник"},
    "unknown_title": {"uz": "Noma'lum", "en": "Not recognized", "ru": "Не распознано"},
    "unknown_hidden": {
        "uz": "Bu taom uchun tekshirilgan ozuqa ma'lumoti yo'q, shuning uchun ko'rsatilmaydi.",
        "en": "No verified nutrition data exists for this dish, so it is not shown.",
        "ru": "Для этого блюда нет проверенных данных о питательности, поэтому оно не отображается.",
    },
    "recognition_failure": {
        "uz": "Taomni ishonch bilan aniqlay olmadik. Yorug'roq va aniqroq rasm bilan urinib ko'ring.",
        "en": "We couldn't confidently identify this dish. Try a clearer photo.",
        "ru": "Не удалось уверенно распознать блюдо. Попробуйте более четкое фото.",
    },
    "unsupported_format": {
        "uz": "Bu fayl formati qo'llab-quvvatlanmaydi. JPG, PNG yoki WEBP dan foydalaning.",
        "en": "This image format isn't supported. Please use JPG, PNG, or WEBP.",
        "ru": "Формат файла не поддерживается. Используйте JPG, PNG или WEBP.",
    },
    "network_error": {
        "uz": "Rasmni tahlil qilishda xatolik yuz berdi. Qayta urinib ko'ring.",
        "en": "Something went wrong while analyzing the image. Please try again.",
        "ru": "Произошла ошибка при анализе изображения. Попробуйте снова.",
    },
    "coarse_warning": {
        "uz": "Taxminiy qiymat — bu raqamlar taom turkumiga tegishli, aniq turiga emas.",
        "en": "Approximate — these figures cover the dish family, not this exact variant.",
        "ru": "Приблизительно — цифры относятся к категории блюда, а не к конкретному варианту.",
    },
    "model_label": {"uz": "Model", "en": "Model", "ru": "Модель"},
    "classes_label": {
        "uz": "Ko'rinadigan sinflar",
        "en": "Visible classes",
        "ru": "Видимые классы",
    },
    "accuracy_label": {"uz": "Test aniqligi", "en": "Test accuracy", "ru": "Точность"},
    "uncalibrated": {
        "uz": "Noma'lum taomni rad etish hali sozlanmagan.",
        "en": "Unknown-dish rejection is not calibrated yet.",
        "ru": "Отклонение неизвестных блюд еще не откалибровано.",
    },
    "waiting": {
        "uz": "Boshlash uchun rasm yuklang.",
        "en": "Upload an image to begin.",
        "ru": "Загрузите изображение, чтобы начать.",
    },
    "loading_uploading": {"uz": "Rasm yuklanmoqda…", "en": "Uploading…", "ru": "Загрузка…"},
    "loading_recognizing": {
        "uz": "AI taomni aniqlamoqda…", "en": "Recognizing the dish…", "ru": "ИИ распознает блюдо…",
    },
    "loading_estimating": {
        "uz": "Ozuqaviy qiymat hisoblanmoqda…",
        "en": "Estimating nutrition…",
        "ru": "Расчет питательной ценности…",
    },
}


def t(key: str, language: str = DEFAULT_LANGUAGE) -> str:
    """Translate one interface key. Falls back to Uzbek, then to the key itself."""
    entry = STRINGS.get(key)
    if entry is None:
        return key
    return entry.get(language) or entry.get(DEFAULT_LANGUAGE) or key


def dish_name(info, language: str = DEFAULT_LANGUAGE) -> str:
    """Pick the dish name for a language from a FoodInfo, falling back to Uzbek."""
    field = NAME_FIELD.get(language, "name_uz")
    return getattr(info, field, None) or info.name_uz
