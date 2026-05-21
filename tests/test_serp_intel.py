from app.services.keyword_difficulty import compute_keyword_difficulty
from app.services.serp_fetcher import fetch_serp
from app.services.serp_intel_bundle import build_serp_keyword_report


def test_fetch_serp_mock_shape() -> None:
    out = fetch_serp("best coffee maker", location="US", device="desktop", num=10)
    assert out["keyword"] == "best coffee maker"
    assert out["source"] in ("mock", "serpapi")
    assert len(out["serp_results"]) == 10
    assert all("position" in r and "url" in r and "domain" in r for r in out["serp_results"])


def test_keyword_report_bundle() -> None:
    rep = build_serp_keyword_report(
        "python asyncio tutorial",
        search_volume=800,
        your_pages=[
            {
                "url": "https://example.com/learn/asyncio",
                "ranking_score": 55.0,
                "pagerank_score": 0.38,
                "word_count": 820,
                "primary_topic": "asyncio",
                "title": "Asyncio tutorial for beginners",
            }
        ],
        crawl_data={},
        topical_authority_score=48.0,
    )
    assert rep["keyword"] == "python asyncio tutorial"
    assert "difficulty" in rep and "simulation" in rep
    assert "probability_top10" in rep["simulation"]
    d = compute_keyword_difficulty(rep["serp_analysis"])
    assert 0 <= d["difficulty_score"] <= 100
