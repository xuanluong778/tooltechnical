from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.queue.celery_app import celery_app
from app.services.internal_linking.crawler import sync_wordpress_site
from app.services.internal_linking.embeddings import embed_chunks_for_site

log = logging.getLogger(__name__)


@celery_app.task(name="internal_links.sync_site", bind=True, max_retries=1)
def task_sync_site(self, wp_site: str, limit_per_type: int = 400) -> dict[str, Any]:
    db: Session = SessionLocal()
    try:
        res = sync_wordpress_site(db=db, wp_site=wp_site, limit_per_type=int(limit_per_type), recreate_chunks=True)
        return {
            "ok": True,
            "wp_site": res.wp_site,
            "fetched": res.fetched,
            "upserted_articles": res.upserted_articles,
            "upserted_chunks": res.upserted_chunks,
        }
    except Exception as exc:
        log.exception("task_sync_site failed wp_site=%s", wp_site)
        return {"ok": False, "error": str(exc)[:900], "wp_site": wp_site}
    finally:
        db.close()


@celery_app.task(name="internal_links.embed_site", bind=True, max_retries=1)
def task_embed_site(self, wp_site: str, model_name: str = "", only_missing: bool = True) -> dict[str, Any]:
    db: Session = SessionLocal()
    try:
        res = embed_chunks_for_site(db=db, wp_site=wp_site, model_name=(model_name or None), only_missing=bool(only_missing))
        return {
            "ok": True,
            "wp_site": wp_site,
            "embedding_model": res.embedding_model,
            "embedded_chunks": res.embedded_chunks,
            "skipped_chunks": res.skipped_chunks,
        }
    except Exception as exc:
        log.exception("task_embed_site failed wp_site=%s", wp_site)
        return {"ok": False, "error": str(exc)[:900], "wp_site": wp_site}
    finally:
        db.close()

