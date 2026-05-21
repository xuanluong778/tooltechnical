from __future__ import annotations

from app.services.ranking_feature_attribution import build_ranking_attribution_report


def test_attribution_bundle_shape() -> None:
    page_row = {
        "url": "https://example.com/a",
        "status": 200,
        "decision": {
            "resolved_signals": {
                "final_indexability": True,
                "js_dependency_level": "low",
                "canonical_valid": True,
            },
            "summary": {"score": 78.0},
        },
        "simulation": {"will_index": True},
        "ranking": {
            "ranking_score": 62.0,
            "graph_metrics": {"in_degree": 4, "pagerank_score": 0.02},
            "content_metrics": {"word_count": 1400, "heading_structure_score": 0.66},
        },
    }
    topical = {
        "authority_score": 0.48,
        "serp_alignment_score": 0.55,
        "serp_intent": {"serp_intent": "informational"},
        "intent_analysis": {"dominant_intent": "informational"},
        "entity_resolution": {"groups": [{"canonical_entity": "widgets"}]},
        "topical_trust": {"trust_score": 0.58},
    }
    serp = {
        "latest": {
            "results": [
                {"rank": 1, "url": "https://other.com/", "title": "Comp A"},
                {"rank": 2, "url": "https://example.com/a", "title": "Us"},
            ]
        }
    }
    out = build_ranking_attribution_report(
        query="best widgets",
        target_url="https://example.com/a",
        page_row=page_row,
        topical_row=topical,
        serp_ground_truth=serp,
        volatility={"normalized_volatility": 0.2},
        data_trust={"fetch_success_rate": 0.9, "render_completeness": 0.95, "duplication_rate": 0.1},
    )
    assert "ranking_probability" in out
    assert out["actual_rank"] == 2
    assert "top_positive" in out["attribution"]
    assert isinstance(out["feature_contributions"], dict)
    assert 0.0 <= out["confidence"] <= 1.0
