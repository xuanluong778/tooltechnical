"""
Parser layer: DOM extraction via BeautifulSoup (structured fields, no regex for core tags).
"""

from __future__ import annotations

from typing import Any

from app.services.structured_parser import parse_structured_html


def parse_html_document(html: str, page_url: str) -> dict[str, Any]:
    """
    Parse rendered HTML into a structured dict (title, meta, H1/H2, images, canonical, robots…).
    """
    return parse_structured_html(html if isinstance(html, str) else "", page_url)
