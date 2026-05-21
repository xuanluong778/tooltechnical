"""Celery tasks: keyword research / clustering (batch, async)."""

from __future__ import annotations

from typing import Any

from app.queue.celery_app import celery_app


def _payload_to_research_kwargs(payload: dict[str, Any]) -> dict[str, Any]:
    seeds = payload.get("seeds") or []
    if not isinstance(seeds, list):
        seeds = []
    seeds = [str(s).strip() for s in seeds if str(s).strip()][:50]
    out: dict[str, Any] = {"seed_keywords": seeds}
    for key in (
        "domain",
        "url",
        "gsc_queries",
        "pages",
        "engine",
        "language",
        "country",
        "device",
        "cluster_mode",
        "cluster_strictness",
        "cluster_fetch_serp",
        "cluster_max_keywords",
    ):
        if key in payload:
            out[key] = payload[key]
    return out


@celery_app.task(name="keywords.research_run", bind=True, max_retries=0)
def run_keyword_research_task(self, payload: dict[str, Any]) -> dict[str, Any]:
    from app.services.keyword_research_pipeline import build_keyword_research_api_response

    kwargs = _payload_to_research_kwargs(payload or {})
    if not kwargs.get("seed_keywords"):
        return {"clusters": [], "meta": {"error": "seed_keyword_required", "task": "keywords.research_run", "entity": "cluster"}}
    return build_keyword_research_api_response(**kwargs)
