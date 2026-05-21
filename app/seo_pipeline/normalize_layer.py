"""
Normalization layer: stable URL identity + idempotent text cleanup on parsed snapshots.
"""

from __future__ import annotations

from typing import Any

from app.services.seo_normalize import normalize_canonical, normalize_text, normalize_url_safe


def normalize_parsed_snapshot(parsed: dict[str, Any], page_url: str) -> dict[str, Any]:
    """
    Clone parsed fields and align URL/canonical with the final normalized page URL.

    Parser already normalizes most text; this layer ties identity to the crawler URL.
    """
    out = dict(parsed)
    nu = normalize_url_safe(page_url) if page_url else ""
    out["url"] = nu or page_url
    can = (out.get("canonical") or "").strip()
    if can:
        out["canonical"] = normalize_canonical(can, nu or page_url)
    out["title"] = normalize_text(out.get("title"))
    out["meta_description"] = normalize_text(out.get("meta_description"))
    out["robots_meta"] = normalize_text(out.get("robots_meta"))
    if isinstance(out.get("h1"), list):
        out["h1"] = [normalize_text(x) for x in out["h1"] if normalize_text(x)]
        out["h1_count"] = len(out["h1"])
    if isinstance(out.get("h2"), list):
        out["h2"] = [normalize_text(x) for x in out["h2"] if normalize_text(x)][:80]
    return out
