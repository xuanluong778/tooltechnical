"""Tests for modular SEO pipeline (normalize, rules wiring, scoring, formatter)."""

from app.seo_pipeline.formatter import enrich_issue_for_output, format_issue_list
from app.seo_pipeline.normalize_layer import normalize_parsed_snapshot
from app.seo_pipeline.parser_layer import parse_html_document
from app.seo_pipeline.pipeline import run_page_pipeline
from app.seo_pipeline.scoring import compute_audit_scores


def test_normalize_parsed_snapshot_canonical() -> None:
    html = '<html><head><link rel="canonical" href="/p/"/></head><body><h1>Hi</h1></body></html>'
    raw = parse_html_document(html, "https://example.com/foo/")
    raw["status"] = 200
    out = normalize_parsed_snapshot(raw, "https://example.com/foo/")
    assert out["url"] == "https://example.com/foo"
    assert out["canonical"].startswith("https://example.com/")


def test_run_page_pipeline_minimal_200() -> None:
    html = """<!DOCTYPE html><html lang="en"><head>
    <title>T</title><meta name="description" content="D">
    <link rel="canonical" href="https://example.com/a">
    </head><body><h1>One</h1><p>word </p></body></html>"""
    r = run_page_pipeline(url="https://example.com/a", status=200, html=html, debug=None)
    assert r.status == 200
    assert r.parsed["title"] == "T"
    types_ = {i["type"] for i in r.issues}
    assert "missing_title" not in types_
    assert "missing_h1" not in types_


def test_scoring_and_formatter() -> None:
    issues = [
        {
            "type": "missing_title",
            "severity": "high",
            "message": "x",
            "confidence": 1.0,
        }
    ]
    s = compute_audit_scores(issues)
    assert 0 <= s.health_score <= 100
    out = format_issue_list(issues)
    assert out[0].get("suggested_fix")
    assert out[0]["checklist_group"] == "Onpage"
    e = enrich_issue_for_output({"type": "robots_unreachable", "severity": "high", "message": "m"})
    assert e["checklist_group"] == "Robots"
