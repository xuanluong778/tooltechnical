"""
Scoring layer: aggregate health score from issues (severity × confidence).
"""

from __future__ import annotations

from typing import Any

from app.seo_pipeline.constants import SEVERITY_WEIGHT
from app.seo_pipeline.types import AuditScoreSnapshot


def compute_audit_scores(issues: list[dict[str, Any]]) -> AuditScoreSnapshot:
    """
    Compute a 0–100 health score. Higher is better.

    Low-confidence issues reduce penalty (fewer false positives drag the score).
    """
    by_severity: dict[str, int] = {"high": 0, "medium": 0, "low": 0}
    weighted_penalty = 0.0
    for issue in issues:
        sev = str(issue.get("severity") or "medium").lower()
        if sev in by_severity:
            by_severity[sev] += 1
        base = float(SEVERITY_WEIGHT.get(sev, 5.0))
        conf = issue.get("confidence")
        try:
            c = float(conf) if conf is not None else 0.72
        except (TypeError, ValueError):
            c = 0.72
        c = max(0.0, min(1.0, c))
        # Issues without confidence (site-level) treated as firm
        weighted_penalty += base * c

    # Asymptotic cap: many issues cannot push below 0 in one shot unrealistically
    health = max(0.0, min(100.0, 100.0 - weighted_penalty * 0.85))
    return AuditScoreSnapshot(
        health_score=round(health, 1),
        weighted_penalty=round(weighted_penalty, 2),
        by_severity=by_severity,
    )
