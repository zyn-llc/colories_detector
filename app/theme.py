"""Design system for the demo: CSS custom properties + light, idempotent JS.

Injected once via st.html near the top of the script. Everything below targets
either Streamlit's documented `key=` class hook (`st-key-<key>`, stable across
reruns and the recommended way to style a specific widget/container) or generic
elements Streamlit already renders (body, headings) -- never brittle, version-specific
internal selectors. If a hook is missing in some Streamlit version, the rule simply
does not match; nothing breaks.

The stylesheet and script live in static/ rather than in string literals here so
they stay editable with CSS/JS tooling and syntax highlighting.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

_STATIC = Path(__file__).parent / "static"


def inject_theme() -> None:
    """Emit the stylesheet and scroll-reveal script. Safe to call once per rerun."""
    st.html(f"<style>{(_STATIC / 'app.css').read_text(encoding='utf-8')}</style>")
    st.html(f"<script>{(_STATIC / 'app.js').read_text(encoding='utf-8')}</script>")


def reveal(html: str) -> str:
    """Wrap a block of HTML so it fades in the first time it scrolls into view."""
    return f'<div class="cai-reveal">{html}</div>'
