"""Enqueue crawl jobs and load completed crawl bundles for the SEO pipeline."""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.crawl_job import DistributedCrawlJob, DistributedCrawlResult

_LOG = logging.getLogger("crawl.queue")


def enqueue_crawl(url: str, project_id: int | None = None, *, max_pages: int = 1) -> dict[str, Any]:
    """
    Persist a job row and dispatch ``process_crawl_job`` to Celery.

    Returns: ``{"job_id", "task_id", "url", "project_id", "max_pages"}``.
    """
    from app.workers.crawl_worker import process_crawl_job

    db = SessionLocal()
    try:
        job = DistributedCrawlJob(
            project_id=project_id,
            job_type="single_url" if max_pages <= 1 else "site",
            target_url=url,
            max_pages=max_pages,
            status="queued",
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        ar = process_crawl_job.apply_async(kwargs={"url": url, "project_id": project_id, "max_pages": max_pages, "distributed_job_id": job.id})
        job.celery_task_id = ar.id
        db.commit()
        _LOG.info(
            "enqueue_crawl",
            extra={"job_id": job.id, "task_id": ar.id, "url": url, "project_id": project_id, "max_pages": max_pages},
        )
        return {"job_id": job.id, "task_id": ar.id, "url": url, "project_id": project_id, "max_pages": max_pages}
    finally:
        db.close()


def fetch_crawl_bundle_for_job(job_id: int, db: Session | None = None) -> dict[str, Any] | None:
    """
    Rebuild ``{pages, edges, domain}`` from stored results for ``analyze_technical_seo`` / pipeline.

    Returns None if job missing or not ``completed``.
    """
    own = db is None
    if own:
        db = SessionLocal()
    assert db is not None
    try:
        job = db.query(DistributedCrawlJob).filter(DistributedCrawlJob.id == job_id).one_or_none()
        if not job or job.status not in ("completed", "partial"):
            return None
        rows = (
            db.query(DistributedCrawlResult)
            .filter(DistributedCrawlResult.job_id == job_id)
            .order_by(DistributedCrawlResult.id.asc())
            .all()
        )
        pages: list[dict[str, Any]] = []
        for r in rows:
            if not r.result_json:
                continue
            try:
                pages.append(json.loads(r.result_json))
            except json.JSONDecodeError:
                continue
        edges: list[dict[str, str]] = []
        seen_e: set[tuple[str, str]] = set()
        for p in pages:
            u = str(p.get("url") or "")
            for link in p.get("internal_links") or []:
                t = str(link)
                key = (u, t)
                if key in seen_e:
                    continue
                seen_e.add(key)
                edges.append({"from": u, "to": t})
        domain = ""
        if pages:
            from urllib.parse import urlparse

            domain = urlparse(str(pages[0].get("url") or "")).netloc or ""
        return {"pages": pages, "total": len(pages), "edges": edges, "domain": domain, "distributed_job_id": job_id}
    finally:
        if own:
            db.close()
