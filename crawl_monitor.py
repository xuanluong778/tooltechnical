"""Shim — implementation lives in ``app.services.crawl_monitor``."""

from app.services.crawl_monitor import record_crawl_outcome, snapshot_metrics, worker_heartbeat

__all__ = ["record_crawl_outcome", "snapshot_metrics", "worker_heartbeat"]
