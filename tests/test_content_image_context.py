"""Tests for context-aware Content AI images."""

from app.services.content_image_context import (
    build_image_prompt_for_section,
    build_image_search_query_for_section,
    build_premium_3d_seo_illustration_prompt,
    build_seo_image_generation_prompt,
    choose_image_placement,
    detect_article_topic,
    extract_image_contexts_from_article,
    normalize_image_style,
    suggest_image_alt_text,
    suggest_image_caption,
)


def test_detect_technical_seo_topic():
    topic = detect_article_topic(
        main_keyword="Technical SEO",
        title="Audit website và Core Web Vitals",
        article_text="crawl schema sitemap indexing",
    )
    assert topic == "technical_seo"


def test_detect_content_seo_topic():
    topic = detect_article_topic(
        main_keyword="Content SEO",
        title="Viết bài blog chuẩn SEO",
        article_text="keyword research outline meta description",
    )
    assert topic == "content_seo"


def test_extract_sections_from_html():
    html = """
    <h2>Technical SEO là gì</h2>
    <p>Phân tích crawl và audit website.</p>
    <h2>Core Web Vitals</h2>
    <p>Tốc độ tải trang và LCP.</p>
    """
    ctx = extract_image_contexts_from_article(article_html=html)
    assert len(ctx) >= 2
    assert "Technical SEO" in ctx[0]["heading"]
    assert "crawl" in ctx[0]["content"].lower()


def test_build_prompt_includes_technical_theme():
    prompt = build_image_prompt_for_section(
        section_heading="Audit website",
        section_content="Kiểm tra crawl log và schema markup",
        main_keyword="Technical SEO",
    )
    assert "audit" in prompt.lower() or "crawl" in prompt.lower()
    assert "dashboard" in prompt.lower() or "SEO" in prompt


def test_build_seo_image_generation_prompt_technical_seo():
    prompt = build_seo_image_generation_prompt(
        main_keyword="technical seo là gì",
        article_title="Technical SEO là gì",
        section_heading="Technical SEO là gì",
        section_summary="crawl, sitemap, schema, tốc độ website",
        image_style="realistic business",
        language="vi",
    )
    assert "technical seo" in prompt.lower() or "Technical SEO" in prompt
    assert "dashboard" in prompt.lower() or "crawl" in prompt.lower()
    assert "no" in prompt.lower() and "logo" in prompt.lower()
    assert len(prompt) <= 3900


def test_normalize_image_styles():
    assert normalize_image_style("3D illustration") == "premium_3d_seo"
    assert normalize_image_style("premium 3d seo") == "premium_3d_seo"
    assert normalize_image_style("modern dashboard") == "modern_dashboard"


def test_build_premium_3d_seo_illustration_prompt():
    prompt = build_premium_3d_seo_illustration_prompt(
        main_keyword="sửa máy tính tận nơi",
        article_title="Sửa máy tính tận nơi TP.HCM",
        section_heading="Dịch vụ sửa máy tính uy tín",
        section_summary="SEO content strategy",
        target_audience="business owners in Vietnam",
    )
    assert "premium 3D illustration" in prompt
    assert "Topic: Sửa máy tính tận nơi TP.HCM" in prompt
    assert "Main keyword: sửa máy tính tận nơi" in prompt
    assert "Section: Dịch vụ sửa máy tính uy tín" in prompt
    assert "16:9 ratio" in prompt
    assert "no watermark" in prompt
    assert "digital marketing workspace" in prompt.lower()


def test_build_seo_prompt_defaults_to_premium_3d():
    prompt = build_seo_image_generation_prompt(
        main_keyword="content seo",
        article_title="Viết bài chuẩn SEO",
        section_heading="Outline bài viết",
    )
    assert "premium 3D illustration" in prompt
    assert "Topic: Viết bài chuẩn SEO" in prompt


def test_alt_text_natural_keyword():
    alt = suggest_image_alt_text(
        {"heading": "Core Web Vitals", "content": "LCP và CLS"},
        "Technical SEO",
    )
    assert "Core Web Vitals" in alt
    assert len(alt) <= 130


def test_choose_placement_h2_indices():
    html = "<h2>A</h2><p>x</p><h2>B</h2><p>y</p><h2>C</h2><p>z</p>"
    placements = choose_image_placement(
        article_html=html,
        max_images=2,
        min_words_between=5,
    )
    assert len(placements) == 2
    assert placements[0]["h2_index"] != placements[1]["h2_index"]


def test_search_query_not_empty():
    q = build_image_search_query_for_section(
        "Audit website",
        "Kiểm tra technical SEO",
        "Technical SEO",
    )
    assert len(q) >= 4
