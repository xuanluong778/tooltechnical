from __future__ import annotations

from app.services.seo_autopilot_bundle import build_seo_autopilot_bundle


def test_autopilot_bundle_keys() -> None:
    core = {
        "version": "v3",
        "indexability": {"indexable_ratio": 0.88, "primary_blockers": []},
        "ranking_decision": {
            "ranking_probability": 0.55,
            "components": {
                "mean_serp_alignment": 0.38,
                "mean_topical_authority": 0.35,
                "mean_ranking_score": 0.5,
            },
        },
        "penalties": [{"type": "serp_misalignment", "impact": -0.12, "reason": "test"}],
        "topical_authority": [
            {
                "topic": "widgets",
                "authority_score": 0.33,
                "serp_alignment_score": 0.4,
                "authority_flow_score": 0.35,
                "serp_intent": {"serp_intent": "commercial"},
                "intent_analysis": {"dominant_intent": "informational"},
                "gap_analysis": {
                    "your_avg_word_count": 400,
                    "competitor_proxy_word_count": 1800,
                    "gap_score": 0.55,
                },
            }
        ],
    }
    gt = {
        "validation": {"actual_best_rank": 12, "misalignment_reasons": ["test hint"], "prediction_error": 0.2},
        "intent_truth": {"dominant_intent": "commercial", "intent_stability_score": 0.5},
        "volatility": {"normalized_volatility": 0.3},
        "data_trust": {"fetch_success_rate": 0.9, "render_completeness": 0.9, "duplication_rate": 0.1},
    }
    out = build_seo_autopilot_bundle(
        core_v3=core,
        ground_truth_bundle=gt,
        queries=["best widgets"],
        monitored_url="https://example.com/p",
        context={"start_url": "https://example.com/p"},
        include_validation_sample=False,
    )
    assert "issues" in out and "top_actions" in out
    assert "quick_wins" in out["roadmap"]
    assert isinstance(out["validation_plan"], list)
    assert isinstance(out["learning_feedback"], list)
