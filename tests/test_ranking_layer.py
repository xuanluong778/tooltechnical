from app.services.content_analysis import analyze_content
from app.services.internal_link_graph import build_link_graph
from app.services.pagerank import compute_pagerank
from app.services.ranking_engine import compute_ranking_score, get_graph_metrics_for_url


def test_build_link_graph_and_pagerank() -> None:
    pages = [
        {
            "url": "https://example.com/",
            "html": '<html><body><a href="/a">a</a></body></html>',
        },
        {
            "url": "https://example.com/a",
            "html": '<html><body><a href="/">home</a></body></html>',
        },
    ]
    g = build_link_graph(pages, entry_urls=["https://example.com/"])
    assert "https://example.com/" in g["nodes"]
    pr = compute_pagerank(g)
    assert len(pr) == 2
    assert 0.0 <= pr["https://example.com/"] <= 1.0
    assert abs(sum(pr.values()) - (pr["https://example.com/"] + pr["https://example.com/a"])) < 1e-6


def test_orphan_and_depth() -> None:
    pages = [
        {"url": "https://ex.com/", "html": '<a href="https://ex.com/b">b</a>'},
        {"url": "https://ex.com/b", "html": "<p>no links</p>"},
        {"url": "https://ex.com/orphan", "html": "<p>x</p>"},
    ]
    g = build_link_graph(pages, entry_urls=["https://ex.com/"])
    assert "https://ex.com/orphan" in g["orphan_urls"]
    assert g["crawl_depth"].get("https://ex.com/b") == 1


def test_analyze_content_heading() -> None:
    html = "<html><body><h1>One</h1><h2>A</h2><h2>B</h2><p>" + ("word " * 400) + "</p></body></html>"
    out = analyze_content(html)
    assert out["word_count"] >= 300
    assert out["content_depth"] in ("normal", "deep")
    assert out["heading_structure_score"] > 0.3


def test_ranking_score_zero_when_not_indexable() -> None:
    r = compute_ranking_score(
        {"indexable": False},
        {"pagerank_score": 1.0, "crawl_depth": 0, "is_orphan": False, "in_degree": 3},
        {"word_count": 500, "content_depth": "normal", "heading_structure_score": 0.8, "keyword_density_estimate": {}},
        {},
    )
    assert r["ranking_score"] == 0.0
    assert r.get("topical_modifiers", {}).get("applied") is False


def test_ranking_topical_boost_and_penalty() -> None:
    data = {
        "indexable": True,
        "technical_score": 72.0,
        "js_dependency_level": "low",
        "cloaking_advanced": {"cloaking_risk_level": "low"},
        "cloaking_risk": False,
        "canonical_valid": True,
    }
    gm = {"pagerank_score": 0.4, "crawl_depth": 1, "is_orphan": False, "in_degree": 2}
    cm = {
        "word_count": 800,
        "content_depth": "normal",
        "heading_structure_score": 0.6,
        "keyword_density_estimate": {"concentration": "low"},
    }
    sim = {"will_index": True, "ranking_eligibility": "high"}
    base = compute_ranking_score(data, gm, cm, sim, topical_signals=None)
    boosted = compute_ranking_score(
        data,
        gm,
        cm,
        sim,
        topical_signals={
            "cluster_authority_normalized": 1.0,
            "topic_relevance_score": 1.0,
            "outside_main_cluster": False,
            "weak_topic_coverage": False,
        },
    )
    assert boosted["topical_modifiers"]["applied"] is True
    assert boosted["ranking_score"] > base["ranking_score"]

    penalized = compute_ranking_score(
        data,
        gm,
        cm,
        sim,
        topical_signals={
            "cluster_authority_normalized": 0.2,
            "topic_relevance_score": 0.2,
            "outside_main_cluster": True,
            "weak_topic_coverage": True,
        },
    )
    assert "outside_dominant_topic_cluster" in penalized["limiting_factors"]
    assert penalized["ranking_score"] < boosted["ranking_score"]


def test_ranking_serp_difficulty_penalty() -> None:
    data = {
        "indexable": True,
        "technical_score": 72.0,
        "js_dependency_level": "low",
        "cloaking_advanced": {"cloaking_risk_level": "low"},
        "cloaking_risk": False,
        "canonical_valid": True,
    }
    gm = {"pagerank_score": 0.4, "crawl_depth": 1, "is_orphan": False, "in_degree": 2}
    cm = {
        "word_count": 800,
        "content_depth": "normal",
        "heading_structure_score": 0.6,
        "keyword_density_estimate": {"concentration": "low"},
    }
    sim = {"will_index": True, "ranking_eligibility": "high"}
    base = compute_ranking_score(data, gm, cm, sim, topical_signals=None)
    hard = compute_ranking_score(
        data,
        gm,
        cm,
        sim,
        topical_signals={"serp_difficulty_score": 80.0},
    )
    assert hard["topical_modifiers"].get("serp_difficulty_applied") is True
    assert hard["ranking_score"] < base["ranking_score"]
    assert "serp_competition_intensity" in hard["limiting_factors"]


def test_get_graph_metrics() -> None:
    pages = [{"url": "https://z.com/", "html": "<p>x</p>"}]
    g = build_link_graph(pages, entry_urls=["https://z.com/"])
    pr = compute_pagerank(g)
    m = get_graph_metrics_for_url(g, "https://z.com/", pr)
    assert m["is_entry_url"] is True
