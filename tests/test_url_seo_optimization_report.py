"""Smoke tests cho báo cáo tối ưu SEO (từ scoreboard)."""

from __future__ import annotations

from app.schemas.url_scoreboard import UrlSeoScoreboardResponse
from app.services.url_seo_optimization_report import build_url_seo_optimization_report


def test_optimization_report_shape_and_playbook():
    sb = {
        "url": "https://example.com/a",
        "normalized_url": "https://example.com/a",
        "fetch": {"ok": True, "status": 200, "final_url": "https://example.com/a", "error": None, "notes": []},
        "scores": {
            "total": 62.0,
            "components": {
                "intent": 45.0,
                "eeat": 70.0,
                "helpful_content": 50.0,
                "structure": 80.0,
                "keyword_semantic": 40.0,
                "ux_readability": 75.0,
                "speed_mobile": 90.0,
                "links": 60.0,
                "schema": 55.0,
                "content_depth": 48.0,
                "freshness": 60.0,
                "ctr": 55.0,
            },
            "weights_applied": {},
        },
        "breakdown": {
            "intent": {
                "keyword": "hosting wordpress",
                "page_intent": {"intent": "informational", "confidence": 0.6},
                "serp_intent": "commercial",
                "signals": [],
            },
            "content_depth": {"word_count": 280, "depth_bucket": "thin", "heading_structure_score": 0.4},
        },
        "issues": [
            {
                "pillar": "intent",
                "type": "intent_mismatch_serp",
                "severity": "medium",
                "priority": "P2",
                "message": "test",
                "fix": "fix intent",
            }
        ],
        "serp": {"keyword": "hosting wordpress", "serp_intent": "commercial"},
        "opportunity": None,
        "weights": {},
        "pillar_definitions": {},
        "page_snapshot": {
            "title": "Giới thiệu dịch vụ của chúng tôi",
            "meta_description": "Chúng tôi cung cấp nhiều giải pháp.",
            "h1_count": 1,
        },
        "generated_at": "2026-01-01T00:00:00+00:00",
    }
    sb["optimization_report"] = build_url_seo_optimization_report(sb)
    UrlSeoScoreboardResponse.model_validate(sb)

    rep = sb["optimization_report"]
    assert "pillar_impact_rank" in rep
    assert rep["pillar_impact_rank"][0]["pillar"] == "intent"
    top = rep["top_problems"][0]
    assert top["type"] == "intent_mismatch_serp"
    assert "before_example" in top and "after_example" in top
    assert top.get("outline_suggestion")
    assert len(rep["checklist"]) >= 1
    assert "checklist_table" in rep
    assert len(rep["checklist_table"]) >= 1
    row0 = rep["checklist_table"][0]
    for k in ("checklist", "danh_gia", "dan_chung_chi_tiet", "giai_phap", "link_tham_khao", "hien_trang", "link_trien_khai", "note"):
        assert k in row0


def test_response_model_accepts_optimization_fields():
    minimal = {
        "url": "https://x.com",
        "normalized_url": "https://x.com",
        "fetch": {},
        "scores": {"total": 50.0, "components": {}},
        "breakdown": {},
        "issues": [],
        "serp": None,
        "opportunity": None,
        "weights": {},
        "pillar_definitions": {},
        "page_snapshot": {},
        "fifteen_pillar_assessment": {},
        "serp_top10_crawl": {},
        "optimization_report": {"checklist": []},
        "generated_at": "2026-01-01T00:00:00+00:00",
    }
    m = UrlSeoScoreboardResponse.model_validate(minimal)
    assert m.optimization_report == {"checklist": []}
