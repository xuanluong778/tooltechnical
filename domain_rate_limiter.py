"""Shim — implementation lives in ``app.services.domain_rate_limiter``."""

from app.services.domain_rate_limiter import acquire_domain_slot

__all__ = ["acquire_domain_slot"]
