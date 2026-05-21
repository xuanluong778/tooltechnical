from app.services.ranking_decision_v3 import build_site_ranking_decision_v3
from app.services.seo_intelligence_core import build_seo_intelligence_core_v3


def test_ranking_decision_v3_basic() -> None:
    out = build_site_ranking_decision_v3(
        technical_health=72.0,
        indexable_ratio=0.9,
        mean_ranking_score_0_100=58.0,
        mean_topical_authority_0_1=0.55,
        mean_serp_alignment=0.62,
        penalties=[],
        trust_weight_adjustment={"serp_alignment": 1.0, "topical_composite": 1.0},
    )
    assert "ranking_probability" in out
    assert 0.0 <= out["ranking_probability"] <= 1.0


def test_seo_intelligence_core_smoke() -> None:
    core = build_seo_intelligence_core_v3(
        page_audits=[],
        technical_summary={"health_score": 70.0},
        site_graph_summary={},
        keyword_intelligence=None,
        topical_authority=[],
        pages=[],
        gsc_queries=None,
        url_serp_overlay={},
        start_url="https://example.com/",
    )
    assert core.get("version") == "v3"
    assert "ranking_decision" in core
    assert "strategy" in core
