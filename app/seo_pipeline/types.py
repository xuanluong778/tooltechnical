"""Typed structures for the SEO analysis pipeline (between layers)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


PageType = Literal["homepage", "article", "category", "landing", "unknown"]
Severity = Literal["high", "medium", "low"]


@dataclass
class CrawlPageRecord:
    """Single URL outcome from the crawler layer (Playwright or HTTP fallback)."""

    url: str
    status: int
    html: str
    response_headers: dict[str, Any] | None = None
    redirect_history: list[str] | None = None
    internal_links: list[str] = field(default_factory=list)


@dataclass
class ParsedDocument:
    """Output of parser + normalization layers (on-page signals)."""

    fields: dict[str, Any]
    source_url: str


@dataclass
class PageRuleContext:
    """Everything the rule engine needs for one URL."""

    url: str
    page_type: PageType
    parsed: dict[str, Any]


@dataclass
class RawEngineIssue:
    """Single check result before API / checklist enrichment."""

    type: str
    severity: Severity
    message: str
    checklist_group: str
    confidence: float
    explanation: str


@dataclass
class PagePipelineResult:
    """End-to-end result for one crawled page (layers 2–5)."""

    url: str
    status: int
    parsed: dict[str, Any]
    page_type: PageType
    issues: list[dict[str, Any]]
    decision_audit: dict[str, Any] | None = None


@dataclass
class AuditScoreSnapshot:
    """Site-level scoring (layer 6)."""

    health_score: float
    weighted_penalty: float
    by_severity: dict[str, int]
