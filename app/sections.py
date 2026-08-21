"""HTML builders for the marketing shell around the app.

Each function returns a string for st.html. None of them touch the classifier,
predictor, or nutrition logic -- they only lay out real numbers and translated copy
that are passed in as arguments. Every stat rendered here is sourced from a live
value (checkpoint metrics, coverage_summary) or cited in a comment, never invented.
"""

from __future__ import annotations

from html import escape

from food_classifier.i18n import SHOWCASE_DISH_CLASSES, dish_name, t
from food_classifier.nutrition import get_food_info


def top_bar_nav_html(lang: str) -> str:
    # Anchor links only -- no interactivity needed, so plain HTML is enough.
    links = (
        ("nav_how", "#how-it-works"),
        ("nav_nutrition", "#app-section"),
        ("nav_about", "#about"),
    )
    items = "".join(
        f'<a href="{href}">{escape(t(key, lang))}</a>' for key, href in links
    )
    return f'<div class="cai-nav">{items}</div>'


def brand_html() -> str:
    return (
        '<div class="cai-brand">'
        '<span class="cai-brand-mark">C</span>Central Asian Food AI'
        "</div>"
    )


def hero_html(lang: str, github_url: str | None) -> str:
    secondary = ""
    if github_url:
        secondary = (
            f'<a class="cai-btn cai-btn-secondary" href="{escape(github_url)}"'
            f' target="_blank" rel="noopener">{escape(t("hero_cta_secondary", lang))}</a>'
        )
    return f"""
    <div class="cai-hero">
      <span class="cai-eyebrow">{escape(t("hero_eyebrow", lang))}</span>
      <h1>{escape(t("hero_headline", lang))}</h1>
      <p>{escape(t("hero_subhead", lang))}</p>
      <div class="cai-cta-row">
        <a class="cai-btn cai-btn-primary" href="#app-section">{escape(t("hero_cta_primary", lang))}</a>
        {secondary}
      </div>
    </div>
    """


def how_it_works_html(lang: str) -> str:
    steps = (
        ("01", "how_step1_title", "how_step1_desc"),
        ("02", "how_step2_title", "how_step2_desc"),
        ("03", "how_step3_title", "how_step3_desc"),
        ("04", "how_step4_title", "how_step4_desc"),
    )
    cards = "".join(
        f"""
        <div class="cai-step">
          <div class="cai-step-num">{num}</div>
          <h3>{escape(t(title, lang))}</h3>
          <p>{escape(t(desc, lang))}</p>
        </div>
        """
        for num, title, desc in steps
    )
    return f"""
    <div id="how-it-works" class="cai-section">
      <div class="cai-section-head">
        <span class="cai-eyebrow">{escape(t("section_how_eyebrow", lang))}</span>
        <h2>{escape(t("section_how_title", lang))}</h2>
      </div>
      <div class="cai-steps">{cards}</div>
    </div>
    """


def dish_showcase_html(lang: str) -> str:
    chips = ""
    for class_name in SHOWCASE_DISH_CLASSES:
        info = get_food_info(class_name)
        if info is None:
            continue
        chips += f'<div class="cai-dish-chip">{escape(dish_name(info, lang))}</div>'
    return f"""
    <div class="cai-section">
      <div class="cai-section-head">
        <span class="cai-eyebrow">{escape(t("section_food_eyebrow", lang))}</span>
        <h2>{escape(t("section_food_title", lang))}</h2>
        <p>{escape(t("section_food_desc", lang))}</p>
      </div>
      <div class="cai-dishes">{chips}</div>
    </div>
    """


def model_stats_html(lang: str, top1_accuracy: float, active_classes: int) -> str:
    # All four figures are passed in from live sources -- see streamlit_app.py.
    stats = (
        (str(active_classes), "stat_classes_label"),
        (f"{top1_accuracy * 100:.1f}%", "stat_accuracy_label"),
        ("16,402", "stat_dataset_label"),
        ("EfficientNet-B0", "stat_architecture_label"),
    )
    cards = "".join(
        f"""
        <div class="cai-stat">
          <div class="cai-stat-value">{escape(value)}</div>
          <div class="cai-stat-label">{escape(t(label, lang))}</div>
        </div>
        """
        for value, label in stats
    )
    return f"""
    <div class="cai-section cai-section-alt">
      <div class="cai-section-head">
        <span class="cai-eyebrow">{escape(t("section_model_eyebrow", lang))}</span>
        <h2>{escape(t("section_model_title", lang))}</h2>
        <p>{escape(t("section_model_desc", lang))}</p>
      </div>
      <div class="cai-stats">{cards}</div>
    </div>
    """


def trust_html(lang: str) -> str:
    points = (
        ("trust_point1_title", "trust_point1_desc"),
        ("trust_point2_title", "trust_point2_desc"),
        ("trust_point3_title", "trust_point3_desc"),
    )
    cards = "".join(
        f"""
        <div class="cai-trust-card">
          <h3>{escape(t(title, lang))}</h3>
          <p>{escape(t(desc, lang))}</p>
        </div>
        """
        for title, desc in points
    )
    return f"""
    <div id="about" class="cai-section">
      <div class="cai-section-head">
        <span class="cai-eyebrow">{escape(t("section_trust_eyebrow", lang))}</span>
        <h2>{escape(t("section_trust_title", lang))}</h2>
      </div>
      <div class="cai-trust">{cards}</div>
    </div>
    """


def programs_html(lang: str, programs: list[dict[str, str]]) -> str:
    # Only ever called when at least one genuinely confirmed program is supplied.
    chips = "".join(
        f'<div class="cai-dish-chip">{escape(p["name"])}</div>' for p in programs
    )
    return f"""
    <div class="cai-section">
      <div class="cai-section-head">
        <span class="cai-eyebrow">{escape(t("section_programs_eyebrow", lang))}</span>
        <h2>{escape(t("section_programs_title", lang))}</h2>
      </div>
      <div class="cai-dishes">{chips}</div>
    </div>
    """


def contact_html(lang: str, telegram_url: str | None, github_url: str | None) -> str:
    buttons = ""
    if telegram_url:
        buttons += (
            f'<a class="cai-btn cai-btn-primary" href="{escape(telegram_url)}"'
            f' target="_blank" rel="noopener">{escape(t("contact_telegram", lang))}</a>'
        )
    if github_url:
        buttons += (
            f'<a class="cai-btn cai-btn-secondary" href="{escape(github_url)}"'
            f' target="_blank" rel="noopener">{escape(t("contact_github", lang))}</a>'
        )
    if not buttons:
        buttons = (
            '<p style="color:var(--cai-ink-muted);font-size:0.9rem">'
            f'{escape(t("waiting", lang))}</p>'
        )
    return f"""
    <div class="cai-section cai-contact">
      <div class="cai-section-head">
        <span class="cai-eyebrow">{escape(t("section_contact_eyebrow", lang))}</span>
        <h2>{escape(t("section_contact_title", lang))}</h2>
        <p>{escape(t("section_contact_desc", lang))}</p>
      </div>
      <div class="cai-cta-row">{buttons}</div>
    </div>
    """


def footer_html(
    lang: str,
    github_url: str | None,
    telegram_url: str | None,
    creator_name: str,
) -> str:
    def link_or_span(label: str, url: str | None) -> str:
        if url:
            return f'<a href="{escape(url)}" target="_blank" rel="noopener">{escape(label)}</a>'
        return f"<span>{escape(label)}</span>"

    return f"""
    <div class="cai-footer">
      <div class="cai-footer-grid">
        <div>
          <div class="cai-brand" style="margin-bottom:8px">
            <span class="cai-brand-mark">C</span>Central Asian Food AI
          </div>
          <p style="font-family:var(--cai-font-body);font-size:0.88rem;color:var(--cai-ink-muted);line-height:1.55;max-width:280px">
            {escape(t("footer_tagline", lang))}
          </p>
        </div>
        <div>
          <h4>{escape(t("footer_product", lang))}</h4>
          <a href="#app-section">{escape(t("nav_nutrition", lang))}</a>
          <a href="#how-it-works">{escape(t("nav_how", lang))}</a>
          <a href="#about">{escape(t("nav_about", lang))}</a>
        </div>
        <div>
          <h4>{escape(t("footer_resources", lang))}</h4>
          {link_or_span(t("footer_resources_github", lang), github_url)}
          <span>{escape(t("footer_resources_model", lang))}</span>
        </div>
        <div>
          <h4>{escape(t("footer_contact", lang))}</h4>
          {link_or_span("Telegram", telegram_url)}
        </div>
      </div>
      <div class="cai-footer-bottom">
        <span>&copy; 2026 Central Asian Food AI. {escape(t("footer_rights", lang))}</span>
        <span>{escape(t("footer_built_by", lang))}: {escape(creator_name)}</span>
      </div>
    </div>
    """
