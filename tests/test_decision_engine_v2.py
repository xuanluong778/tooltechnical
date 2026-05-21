from app.services.decision_engine_v2 import resolve_seo_truth, should_run_rule


def test_resolve_header_overrides_meta() -> None:
    data = {
        "status": 200,
        "parsed": {"robots_meta": "index, follow", "canonical": ""},
        "indexability": {"indexable": True, "indexability_confidence": 0.9},
        "playwright_headers": {"X-Robots-Tag": "noindex"},
        "raw_headers": {},
        "canonical_resolution": {"final_effective_url": "https://ex.com/a", "canonical_url": None},
        "raw_vs_rendered": {"identical": True, "content_length_ratio": 1.0, "raw_length": 100, "rendered_length": 100},
        "js_seo_risk_level": "low",
        "js_dependency": False,
        "url": "https://ex.com/a",
    }
    rs = resolve_seo_truth(data)
    assert rs["final_indexability"] is False
    assert rs["indexability_source"] == "header"


def test_suppress_content_when_not_indexable() -> None:
    rs = {"final_indexability": False}
    ctx = {"status": 200, "redirect_history": []}
    assert should_run_rule("missing_title", rs, ctx) is False
    assert should_run_rule("indexability_blocked", rs, ctx) is True
