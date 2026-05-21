from app.services.search_behavior import (
    detect_signal_conflicts,
    resolve_final_indexability,
    resolve_search_engine_decision,
)


def test_http_404_not_indexable() -> None:
    data = {
        "status": 404,
        "parsed": {"robots_meta": "index, follow"},
        "indexability": {"indexable": True},
        "playwright_headers": {},
        "raw_headers": {},
        "canonical_resolution": {"final_effective_url": "https://ex.com/x"},
        "raw_vs_rendered": {"identical": True, "content_length_ratio": 1.0, "raw_length": 100, "rendered_length": 100},
        "url": "https://ex.com/x",
    }
    r = resolve_final_indexability(data)
    assert r["final_indexable"] is False
    assert r["decision_source"] == "http"
    assert r["confidence"] >= 0.9


def test_header_noindex_overrides_meta_index() -> None:
    data = {
        "status": 200,
        "parsed": {"robots_meta": "index, follow"},
        "indexability": {"indexable": True, "indexability_confidence": 0.95},
        "playwright_headers": {"X-Robots-Tag": "noindex, nofollow"},
        "raw_headers": {},
        "canonical_resolution": {"final_effective_url": "https://ex.com/p"},
        "raw_vs_rendered": {"identical": True, "content_length_ratio": 1.0, "raw_length": 200, "rendered_length": 200},
        "url": "https://ex.com/p",
        "canonical_target_analysis": {
            "fetched": False,
            "similarity_score": None,
            "canonical_chain_valid": True,
            "target_indexable": True,
        },
    }
    d = resolve_search_engine_decision(data)
    assert d["final_indexability"]["final_indexable"] is False
    assert d["final_indexability"]["decision_source"] == "header"
    c = detect_signal_conflicts(data, d["final_indexability"])
    assert isinstance(c["conflicts"], list)
    assert c["severity"] in ("low", "medium", "high")
