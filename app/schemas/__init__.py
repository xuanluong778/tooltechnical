from typing import Any, List, Literal

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    url: str


class TechnicalAnalyzeRequest(BaseModel):
    url: str
    max_pages: int = Field(default=25, ge=1, le=200)


class SEOIssue(BaseModel):
    type: str
    severity: Literal["high", "medium", "low"]
    message: str


class PageSEOResult(BaseModel):
    url: str
    status: int = Field(ge=0)
    title: str
    meta_description: str
    canonical: str
    h1_count: int = Field(ge=0)
    word_count: int = Field(ge=0)
    images_total: int = Field(ge=0)
    images_missing_alt: int = Field(ge=0)
    issues: List[SEOIssue]


class SEOSummary(BaseModel):
    total_pages: int = Field(ge=0)
    total_issues: int
    high: int = Field(ge=0)
    medium: int = Field(ge=0)
    low: int = Field(ge=0)


class AnalyzeResponse(BaseModel):
    pages: List[PageSEOResult]
    summary: SEOSummary


class TechnicalIssue(BaseModel):
    type: str
    severity: Literal["high", "medium", "low"]
    message: str
    url: str | None = None
    checklist_group: str | None = None
    remediation: str | None = None
    suggested_fix: str | None = Field(
        default=None,
        description="Actionable fix text (often same as remediation); output formatter layer.",
    )
    confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="0–1: độ tin cậy rule (cao = ít false positive theo heuristic).",
    )
    explanation: str | None = Field(default=None, description="Lý do ngắn cho audit / so sánh với GSC/SF.")
    page_type: str | None = Field(
        default=None,
        description="homepage | article | category | landing | unknown",
    )
    issue_category: str | None = Field(
        default=None,
        description="Decision layer: indexability | content | technical | structure",
    )
    detected_from: list[str] | None = Field(default=None, description="Signals used by decision rule.")
    possible_causes: list[str] | None = Field(default=None)
    validation_steps: list[str] | None = Field(default=None)
    adjusted_score_impact: float | None = Field(
        default=None,
        description="Weighted score deduction contribution (decision engine v2).",
    )
    decision_source: str | None = Field(default=None, description="e.g. multi_signal_v2")
    suppressed: bool | None = Field(default=None)
    suppression_reason: str | None = Field(default=None)


class BrokenInternalLink(BaseModel):
    url: str
    status: int = Field(ge=0)


class RedirectChainItem(BaseModel):
    url: str
    chain: List[str]
    hops: int = Field(ge=0)


class InternalLinkNode(BaseModel):
    url: str
    inlinks: int = Field(ge=0)
    outlinks: int = Field(ge=0)
    is_orphan_like: bool


class RobotsReport(BaseModel):
    url: str
    status: int = Field(ge=0)
    disallow: List[str]
    sitemaps: List[str]
    allow: List[str] = Field(default_factory=list)
    body_preview: str = ""


class SitemapReport(BaseModel):
    url: str
    status: int = Field(ge=0)
    urls: List[str]


class TechnicalSummary(BaseModel):
    start_url_scheme: str | None = Field(
        default=None,
        description="Giao thức URL bắt đầu quét: https hoặc http (sau normalize_url).",
    )
    start_url_normalized: str | None = Field(
        default=None,
        description="URL bắt đầu đã chuẩn hóa dùng cho crawl (đối chiếu HTTPS/HTTP).",
    )
    broken_internal_links: int = Field(
        ge=0,
        description="Tổng liên kết nội bộ hỏng (4xx/5xx hoặc timeout).",
    )
    broken_internal_404: int = Field(
        default=0,
        ge=0,
        description="Số URL nội bộ trả 404 trong đợt kiểm tra.",
    )
    redirect_chains: int = Field(ge=0)
    internal_pages: int = Field(ge=0)
    total_technical_issues: int = Field(ge=0)
    health_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
        description="0–100 estimated technical health (severity × confidence penalties).",
    )
    weighted_penalty: float | None = Field(
        default=None,
        description="Raw aggregate penalty before mapping to health_score (for tuning).",
    )
    issues_by_severity: dict[str, int] | None = Field(
        default=None,
        description="Count of issues by severity after full audit.",
    )


class TechnicalAnalyzeResponse(BaseModel):
    domain: str
    pages_scanned: int = Field(ge=0)
    audit_id: str | None = Field(
        default=None,
        description="ID bản quét đã lưu (Dashboard) — dùng export CSV/PDF.",
    )
    technical_summary: TechnicalSummary
    broken_internal_links: List[BrokenInternalLink]
    redirect_chains: List[RedirectChainItem]
    internal_link_structure: List[InternalLinkNode]
    robots: RobotsReport
    sitemap: SitemapReport
    issues: List[TechnicalIssue]
    page_audits: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Per URL: url, status, decision (audit sans simulation), simulation, ranking bundle.",
    )
    ranking_priorities: list[dict[str, Any]] = Field(
        default_factory=list,
        description="URLs sorted for remediation (high upside / fixable technical limits).",
    )
    site_graph_summary: dict[str, Any] = Field(
        default_factory=dict,
        description="Counts from internal link graph + PageRank context.",
    )
    keyword_intelligence: dict[str, Any] | None = Field(
        default=None,
        description="Keyword clusters, volumes, intents, URL mappings, opportunities (optional layer).",
    )
    topical_authority: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Per-topic cluster: composite authority, coverage, SERP gap, flow, health, actions.",
    )
    seo_intelligence_core: dict[str, Any] = Field(
        default_factory=dict,
        description="SEO Intelligence Core v3: indexability, ranking_decision, SERP/trust/penalties, strategy.",
    )


class Issue(BaseModel):
    type: str
    severity: str
    message: str
    url: str


class Summary(BaseModel):
    total_issues: int
    high: int
    medium: int
    low: int


class PageResult(BaseModel):
    url: str
    title: str
    h1_count: int


class SingleAnalyzeResponse(BaseModel):
    url: str
    domain: str
    pages_scanned: int
    summary: Summary
    issues: List[Issue]
    pages: List[PageResult]
