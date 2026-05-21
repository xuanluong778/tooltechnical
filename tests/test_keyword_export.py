from __future__ import annotations

from app.services.keyword_export import export_to_excel


def test_export_to_excel_two_sheets() -> None:
    keywords = [
        {"keyword": "a", "intent": "informational", "search_volume": {"avg_monthly": 100}, "difficulty": 0.4},
    ]
    clusters = [
        {"cluster_id": "cluster_1", "main_keyword": "a", "intent": "informational", "keywords": ["a", "b"]},
    ]
    raw = export_to_excel(keywords=keywords, clusters=clusters)
    assert raw[:2] == b"PK"
    assert len(raw) > 200
