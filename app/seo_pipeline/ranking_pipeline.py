"""
Site-level ranking: link graph → PageRank → per-URL bundles for API responses.
"""

from __future__ import annotations

from typing import Any

from app.services.internal_link_graph import build_link_graph
from app.services.pagerank import compute_pagerank
from app.services.ranking_engine import build_page_ranking_bundle, prioritize_pages_for_remediation
from app.services.topical_site_layer import build_topical_layer_for_site
from app.seo_pipeline.types import PagePipelineResult


def split_decision_and_simulation(decision_audit: dict[str, Any] | None) -> tuple[dict[str, Any], dict[str, Any]]:
    """Top-level ``simulation`` vs remainder as ``decision``."""
    audit = dict(decision_audit or {})
    simulation = dict(audit.pop("simulation", {}) or {})
    if not simulation:
        rs = audit.get("resolved_signals")
        if isinstance(rs, dict):
            gs = rs.get("google_simulation")
            if isinstance(gs, dict):
                simulation = dict(gs)
    return audit, simulation


def build_site_ranking_context(pages: list[dict[str, Any]], *, entry_urls: list[str] | None = None) -> dict[str, Any]:
    """Graph + PageRank for the crawled page list."""
    graph = build_link_graph(pages, entry_urls=entry_urls)
    pagerank_scores = compute_pagerank(graph)
    return {"graph": graph, "pagerank": pagerank_scores}


def assemble_page_insight_row(
    *,
    url: str,
    status: int,
    html: str,
    bundle: PagePipelineResult,
    graph: dict[str, Any],
    pagerank_scores: dict[str, float],
    topical_for_url: dict[str, Any] | None = None,
    keyword_signals: dict[str, float] | None = None,
    serp_overlay: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """One API-shaped row: ``url``, ``decision``, ``simulation``, ``ranking``, ``topic``, ``authority``."""
    audit = bundle.decision_audit
    decision, simulation = split_decision_and_simulation(audit)

    topic_out: dict[str, Any] = {}
    authority_out: dict[str, Any] = {}
    topical_signals: dict[str, Any] | None = None
    if topical_for_url:
        topic_out = dict(topical_for_url.get("topic") or {})
        authority_out = dict(topical_for_url.get("authority") or {})
        topical_signals = {
            "cluster_authority_normalized": float(topical_for_url.get("cluster_authority_normalized") or 0.0),
            "topic_relevance_score": float(topical_for_url.get("topic_relevance_score") or 0.0),
            "outside_main_cluster": bool(topical_for_url.get("outside_main_cluster")),
            "weak_topic_coverage": bool(topical_for_url.get("weak_topic_coverage")),
        }
    if keyword_signals:
        ts = dict(topical_signals or {})
        for k in ("keyword_volume_coverage", "keyword_cluster_relevance"):
            if k in keyword_signals:
                ts[k] = float(keyword_signals[k] or 0.0)
        topical_signals = ts

    if serp_overlay:
        ts = dict(topical_signals or {})
        sd = float(serp_overlay.get("serp_difficulty_score") or 0.0)
        if sd > 0:
            ts["serp_difficulty_score"] = sd
            ts["serp_intel_keywords_checked"] = list(serp_overlay.get("keywords_checked") or [])
        topical_signals = ts

    if int(status or 0) != 200 or not (html or "").strip():
        return {
            "url": url,
            "status": int(status or 0),
            "decision": decision,
            "simulation": simulation,
            "topic": topic_out,
            "authority": authority_out,
            "ranking": {
                "ranking_score": 0.0,
                "ranking_potential": "low",
                "limiting_factors": ["non_200_or_empty_document"],
                "strengths": [],
                "why_not_ranking": ["Trang không trả 200 hoặc không có HTML render — không hợp lệ cho ước lượng ranking."],
                "what_to_improve": ["Sửa HTTP và đảm bảo HTML có thể render cho bot."],
                "graph_metrics": {},
                "content_metrics": {},
                "topical_modifiers": {"applied": False},
            },
        }

    ranking = build_page_ranking_bundle(
        url=url,
        graph=graph,
        pagerank_scores=pagerank_scores,
        html=html,
        decision_audit=audit,
        topical_signals=topical_signals,
    )
    return {
        "url": url,
        "status": int(status or 0),
        "decision": decision,
        "simulation": simulation,
        "topic": topic_out,
        "authority": authority_out,
        "ranking": ranking,
    }


def _stub_row(
    url: str,
    status: int,
    graph: dict[str, Any],
    pr: dict[str, float],
    topical_for_url: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from app.services.ranking_engine import get_graph_metrics_for_url

    gmet = get_graph_metrics_for_url(graph, url, pr) if url in (graph.get("nodes") or {}) else {}
    topic_out = dict((topical_for_url or {}).get("topic") or {})
    authority_out = dict((topical_for_url or {}).get("authority") or {})
    return {
        "url": url,
        "status": int(status or 0),
        "decision": {},
        "simulation": {},
        "topic": topic_out,
        "authority": authority_out,
        "ranking": {
            "ranking_score": 0.0,
            "ranking_potential": "low",
            "limiting_factors": ["pipeline_not_run"],
            "strengths": [],
            "why_not_ranking": ["Trang không đủ điều kiện chạy pipeline (HTTP khác 200 hoặc thiếu HTML)."],
            "what_to_improve": ["Đảm bảo URL trả 200 và HTML render để nhận audit đầy đủ."],
            "graph_metrics": gmet,
            "content_metrics": {},
            "topical_modifiers": {"applied": False},
        },
    }


def build_page_insights_for_crawl(
    pages: list[dict[str, Any]],
    staged: list[dict[str, Any]],
    *,
    entry_urls: list[str] | None = None,
    keyword_signals_by_url: dict[str, dict[str, float]] | None = None,
    serp_overlay_by_url: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """
    ``staged`` items: ``url``, ``status``, ``html``, ``bundle`` (``PagePipelineResult``).

    Returns ``(page_insights, ranking_priorities, site_graph_summary)``.
    """
    ctx = build_site_ranking_context(pages, entry_urls=entry_urls)
    graph = ctx["graph"]
    pr = ctx["pagerank"]

    staged_by_url = {str(r.get("url") or ""): r for r in staged if r.get("url")}

    url_to_html: dict[str, str] = {}
    for page in pages:
        u = str(page.get("url") or "").strip()
        if not u:
            continue
        st_row = staged_by_url.get(u)
        h = str(st_row.get("html") or "") if st_row else str(page.get("html") or "")
        url_to_html[u] = h

    topical_layer = build_topical_layer_for_site(
        pages,
        url_to_html=url_to_html,
        graph=graph,
        pagerank=pr,
    )
    per_topical = dict(topical_layer.get("per_url") or {})
    kw_by_url = dict(keyword_signals_by_url or {})
    serp_by_url = dict(serp_overlay_by_url or {})

    rows: list[dict[str, Any]] = []
    for page in pages:
        url = str(page.get("url") or "")
        if not url:
            continue
        st = int(page.get("status") or 0)
        row = staged_by_url.get(url)
        b = row.get("bundle") if row else None
        t_row = per_topical.get(url)
        kw_sig = kw_by_url.get(url)
        serp_ov = serp_by_url.get(url) or serp_by_url.get(url.rstrip("/"))
        if row and isinstance(b, PagePipelineResult):
            rows.append(
                assemble_page_insight_row(
                    url=url,
                    status=st,
                    html=str(row.get("html") or ""),
                    bundle=b,
                    graph=graph,
                    pagerank_scores=pr,
                    topical_for_url=t_row,
                    keyword_signals=kw_sig,
                    serp_overlay=serp_ov,
                )
            )
        else:
            rows.append(_stub_row(url, st, graph, pr, topical_for_url=t_row))

    priorities = prioritize_pages_for_remediation(
        [r for r in rows if int(r.get("status") or 0) == 200]
    )
    summary = {
        "node_count": len(graph.get("nodes") or {}),
        "orphan_count": len(graph.get("orphan_urls") or []),
        "entry_urls": graph.get("entry_urls_normalized") or [],
        "topic_clusters": topical_layer.get("topic_clusters") or {},
        "authority_summary": topical_layer.get("authority_summary") or {},
        "topic_gaps": topical_layer.get("topic_gaps") or {},
        "topical_authority": topical_layer.get("topical_authority") or [],
        "topics_by_url": topical_layer.get("topics_by_url") or {},
    }
    return rows, priorities, summary
