from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.services.serp_top10_crawl import crawl_serp_top_urls


def test_crawl_parses_word_count_and_excludes_self():
    html = "<html><head><title>kw guide</title></head><body><h1>x</h1><p>" + ("word " * 80) + "</p></body></html>"
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = html
    rows = [
        {"url": "https://competitor.com/a", "title": "serp title"},
        {"url": "https://mysite.com/page", "title": "self"},
    ]
    with patch("app.services.serp_top10_crawl.requests.get", return_value=mock_resp):
        out = crawl_serp_top_urls(
            rows,
            exclude_url="https://mysite.com/page",
            keyword="kw guide",
            max_pages=2,
            max_workers=2,
        )
    assert out["stats"]["attempted"] == 1
    assert out["stats"]["successful"] == 1
    assert out["stats"]["median_word_count"] > 50
    assert out["pages"][0]["url"] == "https://competitor.com/a"


def test_crawl_empty_serp():
    out = crawl_serp_top_urls([], exclude_url=None, keyword="x")
    assert out["stats"]["attempted"] == 0
