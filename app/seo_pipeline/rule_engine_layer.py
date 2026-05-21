"""
Rule engine layer: contextual on-page SEO checks (severity, confidence, explanation).
"""

from __future__ import annotations

from typing import Any

from app.services.page_type_detect import PageType
from app.services.technical_rule_engine import build_contextual_onpage_issues


def evaluate_onpage_rules(parsed: dict[str, Any], page_type: PageType, page_url: str) -> list[dict[str, Any]]:
    """
    Run contextual rules for a single page.

    Returns issue dicts without per-page ``url`` (caller attaches for aggregation).
    """
    return build_contextual_onpage_issues(parsed, page_type, page_url)
