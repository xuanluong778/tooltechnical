from __future__ import annotations

from app.services.content_ai_bulk_parse import (
    normalize_bulk_job_items,
    normalize_bulk_outline,
    parse_bulk_input_line,
    parse_bulk_input_text,
)


def test_parse_keyword_only() -> None:
    row = parse_bulk_input_line("viết bài chuẩn seo")
    assert row
    assert row["keyword"] == "viết bài chuẩn seo"
    assert row["custom_title"] == ""


def test_parse_pipe_full_line() -> None:
    line = (
        "dịch vụ seo tổng thể | Dịch vụ SEO tổng thể uy tín | "
        "Giải pháp SEO giúp tăng traffic bền vững | H2: A; H2: B"
    )
    row = parse_bulk_input_line(line)
    assert row
    assert row["keyword"] == "dịch vụ seo tổng thể"
    assert row["custom_title"] == "Dịch vụ SEO tổng thể uy tín"
    assert "traffic" in row["custom_description"]
    assert "## A" in row["custom_outline"]


def test_normalize_bulk_outline_h2() -> None:
    out = normalize_bulk_outline("H2: Dịch vụ SEO là gì; H2: Lợi ích")
    assert "## Dịch vụ SEO là gì" in out
    assert "## Lợi ích" in out


def test_merge_legacy_keywords_and_items() -> None:
    rows = normalize_bulk_job_items(
        keywords=["kw only", "dup"],
        items=[{"keyword": "dup", "custom_title": "Custom"}],
    )
    assert len(rows) == 2
    dup = next(r for r in rows if r["keyword"] == "dup")
    assert dup["custom_title"] == "Custom"
