"""Tests for internal link placement (FAQ skip, spread across sections)."""

from app.services.wp_internal_link_apply import (
    _faq_region_tag_ids,
    _inject_append_context_paragraph,
    _is_reference_append_paragraph,
    apply_merged_internal_links,
)


def test_faq_region_detected():
    html = """
    <h2>Phần A</h2><p>Nội dung A về SEO onpage chi tiết.</p>
    <h2>Câu hỏi thường gặp (FAQ)</h2><p>Hỏi đáp không chèn link.</p>
    """
    soup_ids = _faq_region_tag_ids(__import__("bs4").BeautifulSoup(html, "html.parser"))
    assert len(soup_ids) >= 2


def test_append_spreads_across_sections_not_adjacent():
    html = """
    <h2>Mục 1</h2><p>Đoạn một về chủ đề alpha beta.</p>
    <h2>Mục 2</h2><p>Đoạn hai gamma delta.</p>
    <h2>Mục 3</h2><p>Đoạn ba epsilon zeta.</p>
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    used: set[str] = set()
    sec: dict[str, int] = {}
    faq = _faq_region_tag_ids(soup)
    pos = {id(p): i for i, p in enumerate(soup.find_all("p"))}

    jobs = [
        ("https://ex.com/a", "alpha beta"),
        ("https://ex.com/b", "gamma delta"),
        ("https://ex.com/c", "epsilon zeta"),
    ]
    for url, anchor in jobs:
        ok, _ = _inject_append_context_paragraph(
            soup,
            target_url=url,
            anchor_text=anchor,
            title=anchor,
            used_append_keys=used,
            faq_ids=faq,
            section_insert_counts=sec,
            para_positions=pos,
        )
        assert ok

    ref_ps = [p for p in soup.find_all("p") if _is_reference_append_paragraph(p)]
    assert len(ref_ps) == 3
    # Không hai đoạn tham khảo liên tiếp
    for i in range(len(ref_ps) - 1):
        assert ref_ps[i].find_next_sibling() is not ref_ps[i + 1]


def test_no_link_in_faq_section():
    html = """
    <h2>Giới thiệu</h2><p>Khóa học SEO onpage là gì cho người mới.</p>
    <h2>FAQ</h2><p>Câu hỏi về khóa học SEO onpage là gì.</p>
    """
    out = apply_merged_internal_links(
        content_html=html,
        custom_links=[],
        selected_posts=[
            {
                "link": "https://ex.com/target",
                "anchor_text": "SEO onpage là gì",
                "title": "SEO Onpage",
            }
        ],
        current_url="",
        use_llm_rewrite=False,
        llm_available=False,
        confirmed_append_urls=["https://ex.com/target"],
        apply_mode="full",
    )
    result_html = out["content_html"]
    faq_idx = result_html.lower().find("faq")
    assert faq_idx >= 0
    faq_tail = result_html[faq_idx:]
    assert "<a " not in faq_tail.lower() or "href=" not in faq_tail.lower()
