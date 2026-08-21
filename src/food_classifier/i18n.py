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
    # --- Landing page around the app ----------------------------------------
    "nav_how": {"uz": "Qanday ishlaydi", "en": "How it works", "ru": "Как это работает"},
    "nav_nutrition": {"uz": "Tahlil", "en": "Analyze", "ru": "Анализ"},
    "nav_about": {"uz": "Model haqida", "en": "About", "ru": "О модели"},
    "hero_eyebrow": {
        "uz": "Kompyuter ko'rishi · EfficientNet-B0",
        "en": "Computer vision · EfficientNet-B0",
        "ru": "Компьютерное зрение · EfficientNet-B0",
    },
    "hero_headline": {
        "uz": "Markaziy Osiyo taomlarini rasmdan aniqlang",
        "en": "Identify Central Asian dishes from a photo",
        "ru": "Распознайте блюда Центральной Азии по фото",
    },
    "hero_subhead": {
        "uz": "Rasm yuklang — model taomni aniqlaydi va tekshirilgan manbalarga "
              "asoslangan kaloriya va makronutrient hisobini ko'rsatadi.",
        "en": "Upload a photo — the model names the dish and returns calories and "
              "macronutrients drawn from verified nutrition sources.",
        "ru": "Загрузите фото — модель определит блюдо и рассчитает калории и "
              "макронутриенты по проверенным источникам.",
    },
    "hero_cta_primary": {"uz": "Rasmni sinab ko'ring", "en": "Try a photo", "ru": "Попробовать"},
    "hero_cta_secondary": {"uz": "Kodni ko'rish", "en": "View the code", "ru": "Посмотреть код"},
    "section_how_eyebrow": {"uz": "Jarayon", "en": "Process", "ru": "Процесс"},
    "section_how_title": {
        "uz": "Rasmdan ozuqaviy qiymatgacha",
        "en": "From photo to nutrition",
        "ru": "От фото до питательной ценности",
    },
    "how_step1_title": {"uz": "Rasm yuklang", "en": "Upload", "ru": "Загрузка"},
    "how_step1_desc": {
        "uz": "JPG, PNG yoki WebP. Rasm brauzerdan serverga yuboriladi.",
        "en": "JPG, PNG, or WebP, sent straight from your browser.",
        "ru": "JPG, PNG или WebP — прямо из браузера.",
    },
    "how_step2_title": {"uz": "Tayyorlash", "en": "Preprocess", "ru": "Подготовка"},
    "how_step2_desc": {
        "uz": "224×224 gacha kesiladi va o'qitishdagi kabi normallashtiriladi.",
        "en": "Cropped to 224×224 and normalized exactly as in training.",
        "ru": "Обрезка до 224×224 и нормализация как при обучении.",
    },
    "how_step3_title": {"uz": "Aniqlash", "en": "Classify", "ru": "Классификация"},
    "how_step3_desc": {
        "uz": "EfficientNet-B0 42 sinf bo'yicha ishonch darajasini beradi.",
        "en": "EfficientNet-B0 scores all 42 classes and reports its confidence.",
        "ru": "EfficientNet-B0 оценивает 42 класса и выдает уверенность.",
    },
    "how_step4_title": {"uz": "Hisoblash", "en": "Estimate", "ru": "Расчет"},
    "how_step4_desc": {
        "uz": "Portsiya bo'yicha kaloriya va makronutrientlar hisoblanadi.",
        "en": "Calories and macros are scaled to your portion size.",
        "ru": "Калории и макросы пересчитываются на вашу порцию.",
    },
    "section_food_eyebrow": {"uz": "Taomlar", "en": "Dishes", "ru": "Блюда"},
    "section_food_title": {
        "uz": "Tanilgan taomlar",
        "en": "Dishes it recognizes",
        "ru": "Распознаваемые блюда",
    },
    "section_food_desc": {
        "uz": "Model 42 sinfni chiqaradi; quyidagilar tekshirilgan ozuqaviy "
              "ma'lumotga ega bo'lgan taomlardan namunalar.",
        "en": "The network outputs 42 classes; these are a sample of those with "
              "verified nutrition data attached.",
        "ru": "Модель выдает 42 класса; ниже — примеры блюд с проверенными данными.",
    },
    "section_model_eyebrow": {"uz": "Ko'rsatkichlar", "en": "Performance", "ru": "Показатели"},
    "section_model_title": {
        "uz": "Test to'plamidagi natijalar",
        "en": "Measured on the held-out test set",
        "ru": "Результаты на тестовой выборке",
    },
    "section_model_desc": {
        "uz": "Barcha raqamlar 2 698 ta rasmdan iborat mustaqil test to'plamida "
              "o'lchangan, o'qitishda ishlatilmagan.",
        "en": "Every figure below was measured on 2,698 held-out images the model "
              "never saw during training.",
        "ru": "Все цифры измерены на 2 698 изображениях, не использованных при обучении.",
    },
    "stat_classes_label": {
        "uz": "Ozuqaviy ma'lumotli sinflar",
        "en": "Classes with nutrition",
        "ru": "Классов с данными",
    },
    "stat_accuracy_label": {"uz": "Top-1 aniqlik", "en": "Top-1 accuracy", "ru": "Точность top-1"},
    "stat_dataset_label": {"uz": "O'quv rasmlari", "en": "Training images", "ru": "Изображений"},
    "stat_architecture_label": {"uz": "Arxitektura", "en": "Architecture", "ru": "Архитектура"},
    "section_trust_eyebrow": {"uz": "Metodika", "en": "Method", "ru": "Методика"},
    "section_trust_title": {
        "uz": "Raqamlar qanday olingan",
        "en": "How these numbers were produced",
        "ru": "Как получены эти цифры",
    },
    "trust_point1_title": {
        "uz": "Ikki bosqichli o'qitish",
        "en": "Two-stage training",
        "ru": "Двухэтапное обучение",
    },
    "trust_point1_desc": {
        "uz": "Avval klassifikator boshi, so'ng oxirgi uchta blok ochilib "
              "moslashtirildi — eng yaxshi natija 9-epochda.",
        "en": "The classifier head first, then the last three blocks unfrozen and "
              "fine-tuned — best epoch 9.",
        "ru": "Сначала голова классификатора, затем разморозка трех блоков — лучшая эпоха 9.",
    },
    "trust_point2_title": {
        "uz": "Ajratilgan test to'plami",
        "en": "Held-out test set",
        "ru": "Отложенная выборка",
    },
    "trust_point2_desc": {
        "uz": "Aniqlik o'qitish va validatsiyada ishlatilmagan rasmlarda o'lchandi.",
        "en": "Accuracy is reported on images used for neither training nor validation.",
        "ru": "Точность измерена на изображениях вне обучения и валидации.",
    },
    "trust_point3_title": {
        "uz": "Tekshirilgan ozuqaviy manbalar",
        "en": "Cited nutrition sources",
        "ru": "Проверенные источники",
    },
    "trust_point3_desc": {
        "uz": "Manbasi tasdiqlanmagan taomlar ko'rsatilmaydi — taxminiy raqam "
              "o'rniga halol \"noma'lum\" javobi beriladi.",
        "en": "Dishes without a verified source stay hidden: an honest \"unknown\" "
              "beats an invented number.",
        "ru": "Блюда без проверенного источника скрыты: честное «неизвестно» лучше выдумки.",
    },
    "section_programs_eyebrow": {"uz": "Hamkorlik", "en": "Affiliation", "ru": "Партнерство"},
    "section_programs_title": {"uz": "Dasturlar", "en": "Programs", "ru": "Программы"},
    "section_contact_eyebrow": {"uz": "Aloqa", "en": "Contact", "ru": "Контакты"},
    "section_contact_title": {
        "uz": "Loyiha haqida savollar",
        "en": "Questions about the project",
        "ru": "Вопросы о проекте",
    },
    "section_contact_desc": {
        "uz": "Kod, ma'lumotlar to'plami va o'qitish jarayoni ochiq.",
        "en": "The code, dataset, and training pipeline are all open.",
        "ru": "Код, набор данных и пайплайн обучения открыты.",
    },
    "contact_telegram": {"uz": "Telegram orqali yozish", "en": "Message on Telegram", "ru": "Написать в Telegram"},
    "contact_github": {"uz": "GitHub'da ochish", "en": "Open on GitHub", "ru": "Открыть на GitHub"},
    "footer_tagline": {
        "uz": "Markaziy Osiyo taomlari uchun ochiq kodli tasvir klassifikatori "
              "va ozuqaviy qiymat kalkulyatori.",
        "en": "An open-source image classifier and nutrition calculator for "
              "Central Asian cuisine.",
        "ru": "Открытый классификатор изображений и калькулятор питательности "
              "для блюд Центральной Азии.",
    },
    "footer_product": {"uz": "Mahsulot", "en": "Product", "ru": "Продукт"},
    "footer_resources": {"uz": "Manbalar", "en": "Resources", "ru": "Ресурсы"},
    "footer_resources_github": {"uz": "Manba kodi", "en": "Source code", "ru": "Исходный код"},
    "footer_resources_model": {
        "uz": "EfficientNet-B0 · 42 sinf",
        "en": "EfficientNet-B0 · 42 classes",
        "ru": "EfficientNet-B0 · 42 класса",
    },
    "footer_contact": {"uz": "Aloqa", "en": "Contact", "ru": "Контакты"},
    "footer_rights": {
        "uz": "Barcha huquqlar himoyalangan.",
        "en": "All rights reserved.",
        "ru": "Все права защищены.",
    },
    "footer_built_by": {"uz": "Muallif", "en": "Built by", "ru": "Автор"},
}

#: Dishes shown as chips in the landing-page showcase. Each one is an active class
#: with verified nutrition data, so `get_food_info` never returns None for them.
SHOWCASE_DISH_CLASSES: tuple[str, ...] = (
    "plov",
    "manty",
    "samsa",
    "lagman-w-soup",
    "beshbarmak-w-kazy",
    "shashlyk-chicken",
    "shorpa",
    "naryn",
    "chak-chak",
    "bauyrsak",
    "kurt",
    "achichuk",
)


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
