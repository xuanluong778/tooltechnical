"""editorial_seo_checklist — 18 dòng checklist biên tập."""

from __future__ import annotations

from app.services.editorial_seo_checklist import build_editorial_checklist_table
from app.services.parser import parse_page_seo_data


def test_editorial_returns_18_rows_and_scores():
    html = """<!DOCTYPE html><html><head>
    <title>Hosting WordPress tốt nhất 2026 — So sánh giá</title>
    <meta name="description" content=" """ + ("x" * 150) + """ CTA: xem ngay bảng giá hosting WordPress với ví dụ cấu hình thực tế cho shop.">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    </head><body>
    <h1>Hosting WordPress cho doanh nghiệp</h1>
    <p>Hosting WordPress là nền tảng quan trọng. Ví dụ: shop 500 đơn/ngày cần cache và CDN.</p>
    <h2>Cách chọn hosting</h2>
    <ul><li>Tiêu chí 1</li><li>Tiêu chí 2</li></ul>
    <h2>Câu hỏi thường gặp</h2>
    <p>FAQ câu trả lời ngắn.</p>
    <p>""" + ("word " * 1200) + """</p>
    <h2>Kết luận</h2>
    <p>Tóm lại nên chọn theo ngân sách. Liên hệ ngay để được tư vấn.</p>
    <a href="/ssl">SSL</a>
    <a href="https://wordpress.org/">WP</a>
    <img src="/a.png" alt="Biểu đồ">
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[]}</script>
    </body></html>"""
    pd = parse_page_seo_data(html)
    pkg = build_editorial_checklist_table(
        normalized_url="https://example.com/hosting-wordpress",
        final_url="https://example.com/hosting-wordpress",
        html=html,
        page_data=pd,
        keyword="hosting wordpress",
        serp_intent_pkg={"serp_intent": "commercial"},
        ld_blocks=[{"@type": "FAQPage"}],
        body_word_count=pd.get("word_count") or 0,
    )
    assert len(pkg["rows"]) == 18
    assert len(pkg["items"]) == 18
    assert pkg["average_score"] > 30
    r0 = pkg["rows"][0]
    assert "checklist" in r0 and "danh_gia" in r0
