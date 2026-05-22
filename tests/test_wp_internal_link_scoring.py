"""Tests for internal link relevance scoring and anchor rules."""

from app.services.wp_internal_link_scoring import (
    compute_relevance_score,
    is_bad_anchor,
    suggest_natural_anchor,
    sanitize_anchor,
)
from app.services.wp_internal_link_apply import verify_internal_links_html


def test_bad_anchors_rejected():
    assert is_bad_anchor("xem thêm")
    assert is_bad_anchor("tại đây")
    assert is_bad_anchor("click vào đây")
    assert not is_bad_anchor("dịch vụ SEO tổng thể")


def test_suggested_anchor_from_content():
    html = "<p>Học cách nghiên cứu từ khóa SEO trước khi viết bài.</p>"
    post = {"title": "Cách nghiên cứu từ khóa SEO", "link": "https://ex.com/kw", "slug": "tu-khoa-seo"}
    anchor = suggest_natural_anchor(post=post, content_html=html)
    assert "từ khóa" in anchor.lower() or "nghiên cứu" in anchor.lower()
    assert not is_bad_anchor(anchor)


def test_relevance_score_money_page_boost():
    post = {
        "title": "Dịch vụ SEO tổng thể",
        "link": "https://ex.com/dich-vu-seo/",
        "slug": "dich-vu-seo",
        "category_names": ["SEO"],
        "tag_names": [],
    }
    rel = compute_relevance_score(
        post=post,
        article_primary_keyword="dịch vụ seo",
        article_secondary_keywords="",
        content_plain="Cần tìm dịch vụ seo uy tín cho doanh nghiệp.",
    )
    assert rel["relevance_score"] >= 60
    assert rel["page_type"] in ("money_page", "service")


def test_sanitize_replaces_bad_anchor():
    out = sanitize_anchor(
        "xem thêm",
        post={"title": "Khóa học SEO onpage", "link": "https://ex.com/khoa-hoc"},
        content_html="",
    )
    assert not is_bad_anchor(out)
    assert len(out) >= 4


def test_verify_no_duplicate_url():
    html = """
    <h2>A</h2><p>Xem <a href="https://ex.com/a">alpha</a> và <a href="https://ex.com/a">alpha lại</a>.</p>
    """
    v = verify_internal_links_html(html, jobs=[{"target_url": "https://ex.com/a", "anchor_text": "alpha"}])
    assert not v["ok"]
    assert any("2 lần" in i for i in v["issues"])
