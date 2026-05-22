"""Tests for AI Visual Content Studio prompt + presets."""

from app.services.image_prompt_engine import (
    build_professional_image_prompt,
    build_studio_context_from_project,
    extract_h2_list,
    normalize_brand_tone,
    normalize_image_type,
)
from app.services.image_style_presets import (
    PRESET_FLAT_SAAS,
    PRESET_SEO_3D_PREMIUM,
    list_style_presets,
    normalize_style_preset,
)


def test_normalize_style_preset_aliases():
    assert normalize_style_preset("premium_3d") == PRESET_SEO_3D_PREMIUM
    assert normalize_style_preset("flat") == PRESET_FLAT_SAAS
    assert normalize_style_preset("unknown_xyz") == PRESET_SEO_3D_PREMIUM


def test_list_style_presets_has_six():
    presets = list_style_presets()
    ids = {p["id"] for p in presets}
    assert "seo_3d_premium" in ids
    assert "facebook_ads" in ids
    assert len(presets) >= 6


def test_extract_h2_from_html_and_outline():
    html = "<h2>Huong dan SEO</h2><p>x</p><h2>Link noi bo</h2>"
    outline = "## Tu khoa chinh\n## Checklist"
    h2s = extract_h2_list(html, outline)
    assert "Huong dan SEO" in h2s
    assert "Link noi bo" in h2s
    assert "Tu khoa chinh" in h2s


def test_build_professional_image_prompt_no_text():
    p = build_professional_image_prompt(
        title="Bai viet SEO",
        primary_keyword="seo on page",
        section_heading="Cau truc heading",
        style_preset=PRESET_FLAT_SAAS,
        include_text=False,
    )
    assert "seo on page" in p.lower() or "SEO" in p
    assert "no text" in p.lower() or "NO text" in p


def test_build_studio_context_from_project():
    ctx = build_studio_context_from_project(
        {
            "title": "T",
            "primary_keyword": "kw",
            "content": "<h2>A</h2>",
            "outline_content": "",
            "target_website": "example.com",
        }
    )
    assert ctx["title"] == "T"
    assert ctx["primary_keyword"] == "kw"
    assert "A" in ctx["h2_headings"]


def test_normalize_image_type_and_tone():
    assert normalize_image_type("hero_featured") == "hero_featured"
    assert normalize_image_type("???") == "inline_h2"
    assert normalize_brand_tone("luxury") == "luxury"
    assert normalize_brand_tone("") == "professional"
