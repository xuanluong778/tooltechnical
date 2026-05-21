"""
Pipeline orchestration: Parser → Normalize → Page type → Rule engine (per URL).

Crawler and site-wide checks remain in ``analyzer``; this module owns the on-page chain.
"""

from __future__ import annotations

from typing import Any

from app.services.audit_debug import AuditDebugSession
from app.seo_pipeline.normalize_layer import normalize_parsed_snapshot
from app.seo_pipeline.page_type_layer import classify_page
from app.seo_pipeline.parser_layer import parse_html_document
from app.seo_pipeline.types import PagePipelineResult, PageType
from app.services.seo_rule_engine import issues_to_legacy_api_issues, run_seo_decision_layer


def run_page_pipeline(
    *,
    url: str,
    status: int,
    html: str,
    debug: AuditDebugSession | None = None,
    response_headers: dict[str, Any] | None = None,
    crawl_record: dict[str, Any] | None = None,
) -> PagePipelineResult:
    """
    Execute layers 2–5 for one page with rendered HTML.

    ``parsed["status"]`` is set from the crawl HTTP status (not inferred from HTML).
    """
    raw_parsed = parse_html_document(html, url)
    raw_parsed["status"] = status
    parsed = normalize_parsed_snapshot(raw_parsed, url)
    page_type: PageType = classify_page(url, html, parsed)
    decision_audit = run_seo_decision_layer(
        url,
        parsed,
        page_type,
        crawl_record=crawl_record,
    )
    if debug is not None:
        debug.log_page(
            url,
            rendered_html=html if isinstance(html, str) else "",
            parsed=parsed,
            raw_response_headers=response_headers,
            crawl_record=crawl_record,
            search_behavior=decision_audit.get("search_engine_decision")
            or decision_audit.get("resolved_signals", {}).get("search_engine_decision"),
        )
    issues = issues_to_legacy_api_issues(decision_audit.get("issues") or [], page_type)
    return PagePipelineResult(
        url=url,
        status=status,
        parsed=parsed,
        page_type=page_type,
        issues=issues,
        decision_audit=decision_audit,
    )
