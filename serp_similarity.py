"""Shim — see ``app.services.serp_similarity``."""

from app.services.serp_similarity import compute_serp_similarity, serp_similarity_matrix

__all__ = ["compute_serp_similarity", "serp_similarity_matrix"]
