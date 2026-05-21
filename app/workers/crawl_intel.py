"""Adaptive crawl attempts: domain strategy, proxy selection, classified retries."""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Literal
from urllib.parse import urlparse

from app.services.crawl_quality import compute_crawl_quality
from app.services.domain_intelligence import (
    get_best_crawl_strategy,
    record_domain_crawl_outcome,
    rotate_profile_preference,
)
from app.services.playwright_crawler import crawl_site_detailed_rendered
from app.services.proxy_manager import (
    get_best_proxy,
    mark_proxy_bad,
    mark_proxy_domain_blocked,
    record_proxy_crawl_feedback,
)

_LOG = logging.getLogger(__name__)

OutcomeKind = Literal["ok", "blocked", "timeout", "partial"]


def _host_from_url(url: str) -> str:
    try:
        h = (urlparse(url).hostname or "").lower()
        if h.startswith("www."):
            h = h[4:]
        return h
    except Exception:
        return ""


def classify_bundle(pages: list[dict[str, Any]]) -> OutcomeKind:
    if not pages:
        return "timeout"
    p0 = pages[0]
    st = str(p0.get("crawl_status") or "").lower()
    if st == "blocked":
        return "blocked"
    if st == "timeout":
        return "timeout"
    if str(p0.get("render_status") or "").lower() == "partial" and float(p0.get("render_confidence") or 1) < 0.5:
        return "partial"
    q = compute_crawl_quality(p0)
    if q["quality_level"] == "low" and any(
        f in q["reliability_flags"] for f in ("partial_render", "weak_render_confidence", "timeout")
    ):
        return "partial"
    if str(p0.get("render_status") or "").lower() == "partial" and float(q.get("crawl_quality_score") or 1) < 0.5:
        return "partial"
    return "ok"


def run_intel_crawl(
    url: str,
    max_pages: int,
    *,
    ext_pw: Any,
    ext_br: Any,
) -> tuple[dict[str, Any] | None, str | None]:
    """
    Returns ``(bundle, proxy_server)`` after adaptive attempts, or ``(None, None)`` if exhausted.
    """
    host = _host_from_url(url)
    strategy = get_best_crawl_strategy(host or url)
    profile_pref = str(strategy.get("preferred_profile") or "mobile")
    tscale = float(strategy.get("timeout_strategy", {}).get("initial_scale") or 1.0)
    iscale = float(strategy.get("interaction_delay_scale") or 1.0)
    tmax = float(strategy.get("timeout_strategy", {}).get("max_scale") or 2.6)

    max_intel = int(os.getenv("CRAWL_INTELLIGENCE_MAX_ATTEMPTS", "14"))
    timeout_streak = 0
    partial_retries = 0
    ps: str | None = None
    pu = pp = None
    bundle: dict[str, Any] | None = None

    for _ in range(max_intel):
        if ps is None:
            proxy = get_best_proxy(host or None)
            ps = (proxy or {}).get("server") if proxy else None
            pu = (proxy or {}).get("username") if proxy else None
            pp = (proxy or {}).get("password") if proxy else None

        t0 = time.perf_counter()
        try:
            bundle = crawl_site_detailed_rendered(
                url,
                max_pages=max_pages,
                proxy_server=ps,
                proxy_username=pu,
                proxy_password=pp,
                external_playwright=ext_pw,
                external_browser=ext_br,
                profile_preference=profile_pref,
                timeout_scale=tscale,
                interaction_delay_scale=iscale,
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            if ps:
                record_proxy_crawl_feedback(ps, host, outcome="timeout", response_time_ms=elapsed_ms)
            timeout_streak += 1
            tscale = min(tmax, tscale * 1.22)
            _LOG.debug("intel crawl exception %s (timeout streak=%s): %s", url, timeout_streak, exc)
            if timeout_streak >= int(os.getenv("CRAWL_TIMEOUT_STREAK_PROXY_SWITCH", "3")):
                timeout_streak = 0
                if ps:
                    mark_proxy_bad(ps)
                ps = pu = pp = None
            continue

        timeout_streak = 0
        pages = bundle.get("pages") or []
        kind = classify_bundle(pages)

        if kind == "blocked":
            if ps:
                record_proxy_crawl_feedback(ps, host, outcome="blocked", response_time_ms=elapsed_ms)
                mark_proxy_bad(ps)
                mark_proxy_domain_blocked(host, ps)
            profile_pref = rotate_profile_preference(profile_pref)
            ps = pu = pp = None
            partial_retries = 0
            continue

        if kind == "timeout":
            if ps:
                record_proxy_crawl_feedback(ps, host, outcome="timeout", response_time_ms=elapsed_ms)
            tscale = min(tmax, tscale * 1.18)
            timeout_streak += 1
            if timeout_streak >= int(os.getenv("CRAWL_TIMEOUT_STREAK_PROXY_SWITCH", "3")):
                timeout_streak = 0
                ps = pu = pp = None
            continue

        if kind == "partial":
            if ps:
                record_proxy_crawl_feedback(ps, host, outcome="partial", response_time_ms=elapsed_ms)
            partial_retries += 1
            if partial_retries >= int(os.getenv("CRAWL_PARTIAL_MAX_RETRIES", "3")):
                if ps:
                    record_proxy_crawl_feedback(ps, host, outcome="success", response_time_ms=elapsed_ms)
                return bundle, ps
            iscale = min(2.6, iscale * 1.32)
            tscale = min(tmax, tscale * 1.1)
            profile_pref = rotate_profile_preference(profile_pref)
            continue

        if ps:
            record_proxy_crawl_feedback(ps, host, outcome="success", response_time_ms=elapsed_ms)
        return bundle, ps

    return bundle, ps
