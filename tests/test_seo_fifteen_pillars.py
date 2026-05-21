from __future__ import annotations

from app.services.parser import parse_page_seo_data
from app.services.seo_fifteen_pillars import build_fifteen_pillar_assessment


def test_fifteen_items_and_hard_gate_cap():
    components = {k: 72.0 for k in [
        "intent", "eeat", "helpful_content", "structure", "keyword_semantic",
        "ux_readability", "speed_mobile", "links", "schema", "content_depth",
        "freshness", "ctr",
    ]}
    breakdown = {
        "intent": {"page_intent": {"intent": "informational"}, "serp_intent": "commercial", "score": 72.0, "signals": []},
        "links": {"internal": 2, "external_hosts": 1, "score": 50.0},
        "schema": {"blocks": 1, "valid": True, "score": 80.0},
        "helpful_content": {"lists": 2, "tables": 0, "faq_headings": 1, "score": 70.0},
        "structure": {"h2_count": 4, "score": 75.0},
        "ux_readability": {"avg_sentence_length_words": 18.0, "score": 75.0},
        "ctr": {"title_len": 45, "meta_len": 150, "position_used": 8, "score": 70.0},
        "eeat": {"signals": ["x"]},
        "keyword_semantic": {"signals": ["t1"]},
        "content_depth": {"word_count": 800, "score": 65.0},
        "freshness": {"score": 60.0},
    }
    issues = [{"pillar": "intent", "type": "intent_mismatch_serp", "severity": "medium", "priority": "P2", "message": "x", "fix": "y"}]
    html = "<html><head><title>t</title></head><body><h1>H</h1><p>" + ("w " * 200) + "</p></body></html>"
    pd = parse_page_seo_data(html)
    serp_rows = [{"title": "hosting wordpress cheap", "snippet": "x" * 120} for _ in range(10)]
    out = build_fifteen_pillar_assessment(
        components=components,
        breakdown=breakdown,
        all_issues=issues,
        serp_rows=serp_rows,
        serp_analysis={"competitors": [{"title_quality_score": 0.55 + i * 0.02} for i in range(10)]},
        keyword="hosting wordpress",
        html=html,
        page_data=pd,
        normalized_url="https://ex.com/p",
        our_word_count=400,
    )
    assert len(out["items"]) == 15
    assert out["intent_hard_gate"]["intent_mismatch_issue"] is True
    assert out["total_capped"] <= out["weighted_raw"] + 1.0
