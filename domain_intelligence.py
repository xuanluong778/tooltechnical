"""Shim — see ``app.services.domain_intelligence``."""

from app.services.domain_intelligence import (
    domain_reliability_score,
    get_best_crawl_strategy,
    record_domain_crawl_outcome,
    rotate_profile_preference,
)

__all__ = [
    "domain_reliability_score",
    "get_best_crawl_strategy",
    "record_domain_crawl_outcome",
    "rotate_profile_preference",
]
