"""Shim — implementation lives in ``app.queue.crawl_scheduler``."""

from app.queue.crawl_scheduler import filter_new_urls, mark_urls_seen, schedule_crawl_batch

__all__ = ["filter_new_urls", "mark_urls_seen", "schedule_crawl_batch"]
