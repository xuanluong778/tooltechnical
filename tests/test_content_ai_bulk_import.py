from __future__ import annotations

from app.services.content_ai_bulk_import import (
    parse_bulk_rows_from_table,
    parse_bulk_text_content,
)


def test_parse_table_with_headers() -> None:
    table = [
        ["keyword", "title", "description", "outline", "volume", "content_type", "word_count"],
        ["sửa máy tính", "Title A", "Meta A", "H2: A", "500", "landing", "1200"],
    ]
    rows = parse_bulk_rows_from_table(table)
    assert len(rows) == 1
    assert rows[0]["keyword"] == "sửa máy tính"
    assert rows[0]["custom_title"] == "Title A"
    assert rows[0]["search_volume"] == 500
    assert rows[0]["content_type"] == "landing"
    assert rows[0]["target_word_count"] == 1200


def test_parse_pipe_text() -> None:
    raw = "kw one | T1 | D1 | H2: Sec"
    rows = parse_bulk_text_content(raw)
    assert rows[0]["keyword"] == "kw one"
    assert rows[0]["custom_title"] == "T1"
