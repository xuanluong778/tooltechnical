"""Topical authority AI layer smoke tests."""

from __future__ import annotations

from app.services.internal_link_graph import build_link_graph, evaluate_internal_authority_flow
from app.services.pagerank import compute_pagerank
from app.services.topic_graph import extract_topic_graph, merge_cluster_topic_graphs
from app.services.topical_gap_analysis import analyze_topical_serp_gap, build_cluster_graph_from_pages


def test_extract_topic_graph_shape() -> None:
    html = """
    <html><head><title>Enterprise SEO audit checklist</title></head>
    <body><main><h1>Technical SEO</h1><h2>Crawl budget</h2><h2>Internal links</h2>
    <p>""" + (" ".join(f"paragraph {i} content depth entity graph" for i in range(40))) + """</p>
    </main></body></html>
    """
    g = extract_topic_graph(html)
    assert "nodes" in g and "edges" in g
    assert len(g["nodes"]) >= 3
    assert all("topic" in n and "importance" in n for n in g["nodes"])


def test_merge_graphs() -> None:
    a = extract_topic_graph("<html><title>seo tools</title><body><h1>seo</h1><p>ranking analytics</p></body></html>")
    b = extract_topic_graph("<html><title>seo guide</title><body><h1>seo</h1><p>analytics dashboard</p></body></html>")
    m = merge_cluster_topic_graphs([a, b])
    assert len(m["nodes"]) >= 1


def test_topical_gap_without_serp() -> None:
    cluster = {"topic_label": "seo", "pages": ["https://ex.com/a"], "cluster_size": 1}
    pages_by_url = {
        "https://ex.com/a": {
            "url": "https://ex.com/a",
            "html": "<html><title>seo</title><body><h1>seo</h1><p>" + "word " * 200 + "</p></body></html>",
        }
    }
    ranking_data = {"https://ex.com/a": {"word_count": 400, "content_depth": "normal"}}
    cg = build_cluster_graph_from_pages(["https://ex.com/a"], pages_by_url)
    out = analyze_topical_serp_gap(
        "seo",
        cluster=cluster,
        pages_by_url=pages_by_url,
        ranking_data=ranking_data,
        cluster_graph=cg,
        serp_snapshot=None,
    )
    assert "gap_score" in out and "missing_content_types" in out


def test_evaluate_internal_authority_flow() -> None:
    pages = [
        {
            "url": "https://ex.com/",
            "html": '<a href="https://ex.com/a">page a anchor</a>',
        },
        {
            "url": "https://ex.com/a",
            "html": '<html><head><title>page a title</title></head><body><h1>page a title</h1><p>content</p></body></html>',
        },
    ]
    g = build_link_graph(pages, entry_urls=["https://ex.com/"])
    pr = compute_pagerank(g)
    pages_by_url = {p["url"]: p for p in pages}
    cluster = {"topic_label": "t", "pages": ["https://ex.com/", "https://ex.com/a"], "cluster_size": 2}
    flow = evaluate_internal_authority_flow(cluster, full_graph=g, pages_by_url=pages_by_url, global_pagerank=pr)
    assert "authority_flow_score" in flow
    assert 0.0 <= float(flow["authority_flow_score"]) <= 1.0
