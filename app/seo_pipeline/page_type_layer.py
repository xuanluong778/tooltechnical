"""Page type detection layer (URL + DOM heuristics)."""

from __future__ import annotations

from typing import Any

from app.services.page_type_detect import PageType, detect_page_type


def classify_page(url: str, html: str, parsed: dict[str, Any] | None) -> PageType:
    return detect_page_type(url, html, parsed)
