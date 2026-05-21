"""Shim — see ``app.services.serp_fetcher``."""

from app.services.serp_fetcher import fetch_serp_for_keyword, fetch_serp_for_keyword_async, normalize_serp_url

__all__ = ["normalize_serp_url", "fetch_serp_for_keyword", "fetch_serp_for_keyword_async"]
