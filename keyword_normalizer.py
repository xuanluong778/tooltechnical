"""Shim — see ``app.services.keyword_normalizer``."""

from app.services.keyword_normalizer import normalize_batch, normalize_keyword

__all__ = ["normalize_keyword", "normalize_batch"]
