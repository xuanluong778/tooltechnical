"""Unit tests for SERP layout → page types, intent distribution, mixed label."""

import pytest

from app.services.serp_layout_intent import classify_page_type, infer_serp_layout_intent
from app.services.search_intent import intent_similarity


def test_classify_page_type_blog_and_product():
    assert classify_page_type("https://ex.com/blog/post-1", "How to fix") == "blog"
    assert classify_page_type("https://ex.com/san-pham/item", "") == "product"
    assert classify_page_type("https://www.youtube.com/watch?v=1", "Vid") == "video"


def test_infer_mixed_when_intents_split(monkeypatch):
    monkeypatch.setenv("SERP_INTENT_TOP_SHARE_MIN", "0.48")
    monkeypatch.setenv("SERP_INTENT_SECOND_SHARE_TRIGGER", "0.28")
    monkeypatch.setenv("SERP_PAGE_TYPE_TOP_SHARE_MIN", "0.35")
    snap = {
        "serp_urls": [
            "https://a.com/blog/a",
            "https://a.com/blog/b",
            "https://a.com/blog/c",
            "https://shop.com/san-pham/p1",
            "https://shop.com/san-pham/p2",
        ],
        "titles": ["", "", "", "", ""],
    }
    out = infer_serp_layout_intent(snap)
    assert out is not None
    assert out["mixed_intent"] is True
    assert out["effective_intent"] == "mixed_intent"
    assert sum(out["intent_distribution"].values()) == pytest.approx(1.0, abs=1e-3)
    assert "blog" in out["page_type_distribution"]


def test_infer_homogeneous_transactional(monkeypatch):
    monkeypatch.setenv("SERP_INTENT_TOP_SHARE_MIN", "0.48")
    urls = [f"https://shop.com/san-pham/p{i}" for i in range(10)]
    out = infer_serp_layout_intent({"serp_urls": urls, "titles": [""] * 10})
    assert out is not None
    assert out["mixed_intent"] is False
    assert out["effective_intent"] == "transactional"


def test_intent_similarity_mixed_vs_pure():
    assert intent_similarity("mixed_intent", "mixed_intent") > 0
    assert intent_similarity("mixed_intent", "transactional") < intent_similarity("transactional", "transactional")
    assert intent_similarity("informational", "informational") == 1.0
